import email
import os
import re
from email import policy
from pathlib import Path
from urllib.parse import quote


def extract_images_from_mhtml(msg, image_folder: Path) -> dict:
    """Extract images from MHTML and save to image_folder."""
    image_map = {}
    image_folder.mkdir(parents=True, exist_ok=True)
    for part in msg.walk():
        content_type = part.get_content_type()
        content_id = part.get('Content-ID')
        content_location = part.get('Content-Location')
        if content_type.startswith('image/'):
            ext = content_type.split('/')[-1]
            if content_location:
                img_name = os.path.basename(content_location)
            elif content_id:
                img_name = content_id.strip('<>') + '.' + ext
            else:
                img_name = f'image_{len(image_map)}.{ext}'
            img_path = image_folder / img_name
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                with open(img_path, 'wb') as img_file:
                    img_file.write(payload)
            if content_id:
                image_map[content_id.strip('<>')] = img_path.name
            if content_location:
                image_map[content_location] = img_path.name
    return image_map


def extract_html_from_mhtml(msg) -> str:
    """Extract the HTML part from the MHTML message."""
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            return part.get_content()
    return ''


def update_html_image_references(
        html_content: str, image_map: dict, image_folder_name: str) -> str:
    """Update image src references in HTML to point to extracted images."""

    def replace_img_src(match):
        src = match.group(1)
        key = src[4:] if src.startswith('cid:') else src
        img_file = image_map.get(key, src)
        # Percent-encode the path for browser compatibility
        encoded_path = quote(f'{image_folder_name}/{img_file}')
        return f'src="{encoded_path}"'
    return re.sub(
        r'src=["\"](cid:[^"\"]+|[^"\"]+)["\"]',
        replace_img_src,
        html_content)


def remove_html_comments(html_content: str) -> str:
    """Remove HTML comments from the content."""
    return re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)


def rewrite_links_to_local(
        html_content: str, html_path: str, output_dir: str) -> str:
    """Rewrite all bid3.afry.com links to local HTML file references
    with correct relative paths.
    """
    def repl(match):
        url = match.group(1)
        if url.startswith('https://bid3.afry.com/pages/'):
            local = url[len('https://bid3.afry.com/pages/'):]
            if local.endswith('.html'):
                local = local[:-5]
            # Determine output subfolder and filename
            parts = local.split('/')
            if len(parts) > 1:
                folder = parts[0]
                filename = '_'.join(parts[1:]) + '.html'
                # If current HTML file is in the same subfolder,
                # use only filename
                current_folder = os.path.relpath(
                    os.path.dirname(html_path), output_dir)
                if current_folder == folder:
                    return f'href="{filename}"'
                else:
                    return f'href="{folder}_{filename}"'
            else:
                # No subfolder, just filename
                filename = parts[0] + '.html'
                return f'href="{filename}"'
        return match.group(0)
    html_content = re.sub(
        r'href=["\"](https://bid3.afry.com/pages/[^"\"]+)["\"]',
        repl, html_content)
    return html_content


def convert_mhtml_to_html(mhtml_path: str, html_path: str) -> None:
    """Convert an .mhtml file to .html by extracting HTML and images."""
    try:
        with open(mhtml_path, 'rb') as f:
            raw = f.read()
        msg = email.message_from_bytes(raw, policy=policy.default)
        html_dir = Path(html_path).parent
        image_folder_name = Path(html_path).stem + '_images'
        image_folder = html_dir / image_folder_name
        image_map = extract_images_from_mhtml(msg, image_folder)
        html_content = extract_html_from_mhtml(msg)
        if not html_content:
            raise ValueError('No HTML content found in file: ' + mhtml_path)
        html_content = update_html_image_references(
            html_content, image_map, image_folder_name
        )
        html_content = remove_html_comments(html_content)
        html_content = rewrite_links_to_local(
            html_content, str(html_path), str(Path(html_path).parents[1])
        )
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f'Error converting {mhtml_path}: {e}')


def batch_convert_mhtml_to_html(input_dir: str, output_dir: str) -> None:
    """
    Loop through all .mhtml files in input_dir, convert them to .html, and
    save in output_dir.

    Parameters:
    input_dir (str): Directory containing .mhtml files.
    output_dir (str): Directory to save .html files.
    """
    # Delete all contents of the output directory
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    else:
        os.makedirs(output_dir)

    # Recursively process all .mhtml files in input_dir and subfolders
    for dirpath, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.mhtml'):
                mhtml_path = os.path.join(dirpath, filename)
                # Preserve subfolder structure in output
                rel_dir = os.path.relpath(dirpath, input_dir)
                out_dir = (
                    os.path.join(output_dir, rel_dir)
                    if rel_dir != '.' else output_dir)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                html_filename = os.path.splitext(filename)[0] + '.html'
                html_path = os.path.join(out_dir, html_filename)
                convert_mhtml_to_html(mhtml_path, html_path)
                print(
                    f'Converted: {os.path.relpath(mhtml_path, input_dir)}'
                    f' -> {os.path.relpath(html_path, output_dir)}')


if __name__ == '__main__':
    batch_convert_mhtml_to_html('output', 'html')
