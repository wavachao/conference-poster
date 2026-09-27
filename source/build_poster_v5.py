from pathlib import Path
import base64, copy, html, io, subprocess, re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.graphics.barcode import qr
from pypdf import PdfReader, PdfWriter, Transformation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
ASSETS = ROOT / 'source' / 'assets'
TMP = ROOT / 'tmp' / 'pdfs'
for d in [OUT, ASSETS, TMP]: d.mkdir(parents=True, exist_ok=True)
MM = 72 / 25.4
W, H = 841, 1189
NAVY, TEAL, INK, MUTED = '#163846', '#16766D', '#263640', '#63727B'
PALE, RULE, WHITE = '#EDF5F2', '#D6DFE2', '#FFFFFF'
for name, filename in [('Segoe','segoeui.ttf'),('Segoe-Semibold','seguisb.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + filename))
paper = PdfReader(ROOT / '3767308.3835710.pdf')

# Preserve the original vector diagram, without its caption or page header.
crop = (70, 87, 553, 299)  # left, top, right, bottom in paper points
cp = copy.deepcopy(paper.pages[3])
left, top, right, bottom = crop
cp.add_transformation(Transformation().translate(-left, -(792-bottom)))
cp.mediabox.lower_left = (0, 0)
cp.mediabox.upper_right = (right-left, bottom-top)
cp.cropbox = copy.deepcopy(cp.mediabox)
wr = PdfWriter(); wr.add_page(cp)
with open(ASSETS / 'method.pdf', 'wb') as f: wr.write(f)
subprocess.run(['pdftocairo','-svg',str(ASSETS/'method.pdf'),str(ASSETS/'method.svg')],check=True)
for i, im in enumerate(paper.pages[5].images):
    (ASSETS / ['qualitative_coco.jpg','qualitative_fss.jpg'][i]).write_bytes(im.data)

c = canvas.Canvas(str(TMP/'poster_base.pdf'), pagesize=(W*MM,H*MM))
c.setTitle('SegmentGDA - ACM Multimedia 2026 Poster')
c.setAuthor('Yiqi Wu, Huachao Wu, Ronglei Hu, Dejun Zhang')
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="841mm" height="1189mm" viewBox="0 0 841 1189">']

def rect(x,y,w,h,fill):
    c.setFillColor(HexColor(fill)); c.rect(x*MM,(H-y-h)*MM,w*MM,h*MM,stroke=0,fill=1)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')

def line(x,y,x2,y2,color=RULE,width=0.5):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width*MM)
    c.line(x*MM,(H-y)*MM,x2*MM,(H-y2)*MM)
    svg.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')

def text(x,y,s,size=28,bold=False,color=INK,anchor='start'):
    font='Segoe-Semibold' if bold else 'Segoe'
    c.setFont(font,size);c.setFillColor(HexColor(color))
    runs=[]; pos=0
    for match in re.finditer(r'(?:COCO-20|LVIS-92|PASCAL-5)i',s):
        runs.extend([(s[pos:match.end()-1],False),('i',True)]);pos=match.end()
    runs.append((s[pos:],False))
    tw=sum(pdfmetrics.stringWidth(t,font,size*(.7 if sup else 1)) for t,sup in runs)
    tx=c.beginText(x*MM-tw*{'start':0,'middle':.5,'end':1}[anchor],(H-y)*MM)
    parts=[]
    for t,sup in runs:
        tx.setFont(font,size*(.7 if sup else 1));tx.setRise(size*.35 if sup else 0);tx.textOut(t)
        parts.append(f'<tspan baseline-shift="super" font-size="70%">{html.escape(t)}</tspan>' if sup else html.escape(t))
    c.drawText(tx)
    svg.append(f'<text x="{x}" y="{y}" font-family="Segoe UI, sans-serif" font-size="{size/MM}" font-weight="{600 if bold else 400}" fill="{color}" text-anchor="{anchor}">{"".join(parts)}</text>')

def para(x,y,s,width,size=28,bold=False,color=INK,leading=12):
    font='Segoe-Semibold' if bold else 'Segoe'
    words=s.split(); current=''; rows=[]
    for word in words:
        candidate=(current+' '+word).strip()
        if pdfmetrics.stringWidth(candidate,font,size)>width*MM and current:
            rows.append(current);current=word
        else: current=candidate
    if current: rows.append(current)
    for i,row in enumerate(rows):text(x,y+i*leading,row,size,bold,color)
    return y+len(rows)*leading

def heading(x,y,num,title,width):
    text(x,y,title,43,True,NAVY)
    line(x,y+9,x+width,y+9,RULE,.45)

def raster(x,y,w,h,path):
    c.drawImage(str(path),x*MM,(H-y-h)*MM,w*MM,h*MM)
    data=base64.b64encode(path.read_bytes()).decode()
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/jpeg;base64,{data}"/>')

rect(0,0,W,H,WHITE)
rect(26,0,789,3,TEAL)
text(26,20,'ACM MULTIMEDIA 2026',26,True,TEAL)
text(815,20,'10-14 NOVEMBER 2026   /   RIO DE JANEIRO',22,False,MUTED,'end')
text(26,54,'SegmentGDA: Training-Free Few-Shot Segmentation',72,True,NAVY)
text(26,84,'via Gaussian Discriminant Analysis on Vision Foundation Features',60,True,NAVY)
text(26,109,'Yiqi Wu*    Huachao Wu*    Ronglei Hu    Dejun Zhang',35,False,INK)
text(26,127,'School of Computer Science, China University of Geosciences, Wuhan, China',29,False,MUTED)
line(26,140,815,140,RULE,.6)

heading(26,161,'01','Motivation',377)
para(26,184,'Segment a novel object from only a few annotated support examples.',377,35,leading=14)
para(26,217,'Local patch matching can miss object parts and select background clutter.',377,33,color=INK,leading=13)
heading(439,161,'02','Core idea',376)
para(439,184,'Model foreground and background as distributions in frozen foundation features.',376,36,True,color=TEAL,leading=14)
para(439,217,'Bayesian posteriors guide SAM prompts. No task-specific training or fine-tuning.',376,33,color=INK,leading=13)

heading(26,260,'03','Method overview',789)
# The final PDF overlays the original vector diagram in this rectangle.
mx,my,mw = 46,278,749
mh=mw*(bottom-top)/(right-left)
method_svg=base64.b64encode((ASSETS/'method.svg').read_bytes()).decode()
svg.append(f'<image x="{mx}" y="{my}" width="{mw}" height="{mh}" xlink:href="data:image/svg+xml;base64,{method_svg}"/>')
text(26,628,'1  Frozen features',34,True,NAVY)
para(26,647,'DINOv2 ViT-L/14 features, signed square-root transform and L2 normalization.',239,32,leading=13)
text(301,628,'2  Gaussian inference',34,True,NAVY)
para(301,647,'Two class means and a shared covariance yield patch-level foreground posteriors.',239,32,leading=13)
text(576,628,'3  SAM refinement',34,True,NAVY)
para(576,647,'Diverse positive and negative points guide frozen SAM ViT-H to iteratively correct errors.',239,32,leading=13)

heading(26,694,'04','5-shot comparison with training-free methods',789)
text(26,717,'mIoU (%)    Selected baselines from Tables 1-2 of the paper',27,False,MUTED)
tablex=[33,248,346,439,531]
line(26,727,567,727,NAVY,.7)
line(26,748,567,748,NAVY,.45)
for j,(x,s) in enumerate(zip(tablex,['Method','COCO-20i','FSS-1000','LVIS-92i','PASCAL-5i'])):
    text(x,742,s,29,True,NAVY,'start' if j==0 else 'middle')
rows=[('Matcher','60.7','89.6','40.0','74.0'),
      ('UNICL-SAM','78.7','86.3','37.4','-'),
      ('GF-SAM','66.8','88.9','44.2','82.6'),
      ('SegmentGDA (ours)','62.5','89.8','41.8','82.2')]
best={(1,1),(3,2),(2,3),(2,4)}
for i,row in enumerate(rows):
    yy=748+i*21
    if i==3:rect(26,yy,541,21,PALE)
    for j,(x,s) in enumerate(zip(tablex,row)):
        is_best=(i,j) in best
        text(x,yy+15,s,33,is_best or (i==3 and j==0),TEAL if i==3 else INK,'start' if j==0 else 'middle')
    if i==3:line(26,yy+21,567,yy+21,NAVY,0.5)
text(26,846,'Bold: best among the methods shown.  -: not reported in our paper.',24,False,MUTED)
para(595,735,'Higher than Matcher on all four benchmarks; competitive on FSS-1000 and PASCAL-5i.',220,33,True,TEAL,14)
para(595,798,'Single-example performance remains a limitation; the main gains occur with multiple supports.',220,29,False,MUTED,12)
text(26,865,'Our 1-shot mIoU, in the same dataset order: 42.1 / 82.9 / 26.2 / 59.5.',28,False,MUTED)

heading(26,894,'05','Qualitative comparisons',789)
text(26,919,'COCO-20i',34,True,NAVY)
text(435,919,'FSS-1000',34,True,NAVY)
raster(26,930,380,380*1030/2062,ASSETS/'qualitative_coco.jpg')
raster(435,930,380,380*1030/2062,ASSETS/'qualitative_fss.jpg')
text(26,1132,'Rows: ground truth / Matcher / GF-SAM / SegmentGDA. Selected 5-shot episodes.',25,False,MUTED)

line(26,1140,751,1140,RULE,.6)
text(26,1153,'TAKEAWAY',25,True,TEAL)
text(105,1153,'Global statistics improve multi-shot mask transfer.',30,True,NAVY)
text(26,1166,'* Equal contribution.  Correspondence: zhangdejun@cug.edu.cn',23,False,MUTED)
text(797,1166,'CODE',18,True,TEAL,'middle')

# A vector QR code remains sharp at print scale.
codeurl='https://github.com/wavachao/SegmentGDA'
widget=qr.QrCodeWidget(codeurl,barLevel='M'); widget.qr.make()
matrix=widget.qr.modules; n=len(matrix); unit=32/(n+8)
rect(781,1126,32,32,WHITE)
for row,cells in enumerate(matrix):
    for col,on in enumerate(cells):
        if on:rect(781+(col+4)*unit,1126+(row+4)*unit,unit,unit,NAVY)
c.linkURL(codeurl,(775*MM,(H-1166)*MM,815*MM,(H-1126)*MM),relative=0)
svg.append('</svg>')
(OUT/'SegmentGDA_ACMMM2026_A0_v5_editable.svg').write_text('\n'.join(svg),encoding='utf-8')
c.showPage();c.save()

base=PdfReader(TMP/'poster_base.pdf').pages[0]
method=PdfReader(ASSETS/'method.pdf').pages[0]
scale=mw*MM/(right-left)
base.merge_transformed_page(method,Transformation().scale(scale).translate(mx*MM,(H-my-mh)*MM))
final=PdfWriter();final.add_page(base)
final.add_metadata({'/Title':'SegmentGDA | ACM Multimedia 2026 | A0 portrait','/Author':'Yiqi Wu; Huachao Wu; Ronglei Hu; Dejun Zhang'})
with open(OUT/'SegmentGDA_ACMMM2026_A0_v5.pdf','wb') as f:final.write(f)
print('Created A0 PDF and editable SVG.')
