import subprocess
import sys
import tempfile
import os

from bs4 import BeautifulSoup

def get_max(soup, name):
    max_y = 0
    for p in soup.find_all('use'):
        max_y = max(float(p[name]), max_y)
    return (max_y)

def crop_svg(old_svg_fname, new_svg_fnae):
    soup = BeautifulSoup(open(old_svg_fname).read(), 'html.parser')
    base_attrs = soup.find("svg").attrs
    viewBox = base_attrs['viewbox']
    xs,ys,xe,ye = viewBox.split()
    xe = float(xe)
    ye = float(ye)
    ye = min(ye, get_max(soup, 'y') + 30)
    xe = min(xe, get_max(soup, 'x') + 30)
    new_box = f"{xs} {ys} {xe} {ye}"
    base_attrs['viewbox'] = new_box
    base_attrs['width'] = f"{xe}px"
    base_attrs['height'] = f"{ye}px"
    with open(new_svg_fnae, "w") as outf:
        outf.write(str(soup))

def build_svg(tex_fname, svg_fname):
    svg_fname = os.path.abspath(svg_fname)
    with open(tex_fname,'rb') as orig_file, \
        tempfile.NamedTemporaryFile(suffix=".tex") as alt_file, \
        tempfile.TemporaryDirectory() as workdir:
        alt_file.write(b"\\nonstopmode\n")
        alt_file.write(orig_file.read())
        alt_file.flush()
        subprocess.run(f"cd {workdir} && pdflatex {alt_file.name}", shell=True)
        alt_file_pdf = os.path.join(workdir,os.path.basename(alt_file.name)[:-3] + "pdf")
        scratch_svg_name = f"{alt_file_pdf}.svg"
        subprocess.run(f"pdf2svg {alt_file_pdf} {scratch_svg_name}", shell=True)
        crop_svg(scratch_svg_name, svg_fname)


if __name__ == "__main__":
    assert len(sys.argv) == 3,  "requires 2 arguments, tex_fname, svg_fname"
    build_svg(sys.argv[1], sys.argv[2])
