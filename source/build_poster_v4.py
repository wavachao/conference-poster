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
text(26,23,'ACM MULTIMEDIA 2026',26,True,TEAL)
text(815,23,'10-14 NOVEMBER 2026   /   RIO DE JANEIRO',22,False,MUTED,'end')
text(26,63,'SegmentGDA: Training-Free Few-Shot Segmentation',72,True,NAVY)
text(26,95,'via Gaussian Discriminant Analysis on Vision Foundation Features',60,True,NAVY)
text(26,127,'Yiqi Wu*    Huachao Wu*    Ronglei Hu    Dejun Zhang',35,False,INK)
text(26,147,'School of Computer Science, China University of Geosciences, Wuhan, China',29,False,MUTED)
line(26,164,815,164,RULE,.6)

heading(26,188,'01','Motivation',377)
para(26,213,'Segment a novel object from only a few annotated support examples.',377,36,leading=15)
para(26,253,'Local patch matching can miss object parts and select background clutter.',377,34,color=INK,leading=14)
heading(439,188,'02','Core idea',376)
para(439,213,'Model foreground and background as distributions in frozen foundation features.',376,37,True,color=TEAL,leading=15)
para(439,253,'Bayesian posteriors guide SAM prompts. No task-specific training or fine-tuning.',376,34,color=INK,leading=14)

heading(26,311,'03','Method overview',789)
# The final PDF overlays the original vector diagram in this rectangle.
mx,my,mw = 26,331,570
mh=mw*(bottom-top)/(right-left)
method_svg=base64.b64encode((ASSETS/'method.svg').read_bytes()).decode()
svg.append(f'<image x="{mx}" y="{my}" width="{mw}" height="{mh}" xlink:href="data:image/svg+xml;base64,{method_svg}"/>')
text(619,345,'1  Frozen features',34,True,NAVY)
para(619,366,'DINOv2 ViT-L/14 features, signed square-root transform and L2 normalization.',196,32,leading=13.5)
text(619,429,'2  Gaussian inference',33,True,NAVY)
para(619,450,'Two class means and a shared covariance yield patch-level foreground posteriors.',196,32,leading=13.5)
text(619,519,'3  SAM refinement',34,True,NAVY)
para(619,540,'Diverse positive and negative points guide frozen SAM ViT-H to iteratively correct errors.',196,32,leading=13.5)

heading(26,612,'04','5-shot comparison with training-free methods',789)
text(26,638,'mIoU (%)    Selected baselines from Tables 1-2 of the paper',30,False,MUTED)
tablex=[36,337,489,641,767]
line(26,649,815,649,NAVY,.7)
line(26,672,815,672,NAVY,.45)
for j,(x,s) in enumerate(zip(tablex,['Method','COCO-20i','FSS-1000','LVIS-92i','PASCAL-5i'])):
    text(x,665,s,32,True,NAVY,'start' if j==0 else 'middle')
rows=[('Matcher','60.7','89.6','40.0','74.0'),
      ('UNICL-SAM','78.7','86.3','37.4','-'),
      ('GF-SAM','66.8','88.9','44.2','82.6'),
      ('SegmentGDA (ours)','62.5','89.8','41.8','82.2')]
best={(1,1),(3,2),(2,3),(2,4)}
for i,row in enumerate(rows):
    yy=672+i*24
    if i==3:rect(26,yy,789,24,PALE)
    for j,(x,s) in enumerate(zip(tablex,row)):
        is_best=(i,j) in best
        text(x,yy+17,s,36,is_best or (i==3 and j==0),TEAL if i==3 else INK,'start' if j==0 else 'middle')
    if i==3:line(26,yy+24,815,yy+24,NAVY,0.5)
text(26,784,'Bold: best among the methods shown.  -: not reported in our paper.',26,False,MUTED)
text(26,807,'Higher than Matcher on all four benchmarks; competitive on FSS-1000 and PASCAL-5i.',32,True,TEAL)
text(26,833,'Our 1-shot mIoU, in the same dataset order: 42.1 / 82.9 / 26.2 / 59.5.',29,False,MUTED)
text(26,849,'Single-example performance remains a limitation; the main gains occur with multiple supports.',29,False,MUTED)

heading(26,880,'05','Qualitative comparisons',789)
text(26,905,'COCO-20i',34,True,NAVY)
text(435,905,'FSS-1000',34,True,NAVY)
raster(26,916,380,380*1030/2062,ASSETS/'qualitative_coco.jpg')
raster(435,916,380,380*1030/2062,ASSETS/'qualitative_fss.jpg')
text(26,1121,'Rows: ground truth / Matcher / GF-SAM / SegmentGDA. Selected 5-shot episodes.',27,False,MUTED)

line(26,1135,815,1135,RULE,.6)
text(26,1152,'TAKEAWAY',27,True,TEAL)
text(110,1152,'Global statistics improve multi-shot mask transfer.',33,True,NAVY)
text(26,1177,'* Equal contribution.  Correspondence: zhangdejun@cug.edu.cn',26,False,MUTED)
text(795,1183,'CODE',18,True,TEAL,'middle')

# A vector QR code remains sharp at print scale.
codeurl='https://github.com/wavachao/SegmentGDA'
widget=qr.QrCodeWidget(codeurl,barLevel='M'); widget.qr.make()
matrix=widget.qr.modules; n=len(matrix); unit=36/(n+8)
rect(777,1139,36,36,WHITE)
for row,cells in enumerate(matrix):
    for col,on in enumerate(cells):
        if on:rect(777+(col+4)*unit,1139+(row+4)*unit,unit,unit,NAVY)
c.linkURL(codeurl,(775*MM,(H-1186)*MM,815*MM,(H-1137)*MM),relative=0)
svg.append('</svg>')
(OUT/'SegmentGDA_ACMMM2026_A0_v4_editable.svg').write_text('\n'.join(svg),encoding='utf-8')
c.showPage();c.save()

base=PdfReader(TMP/'poster_base.pdf').pages[0]
method=PdfReader(ASSETS/'method.pdf').pages[0]
scale=mw*MM/(right-left)
base.merge_transformed_page(method,Transformation().scale(scale).translate(mx*MM,(H-my-mh)*MM))
final=PdfWriter();final.add_page(base)
final.add_metadata({'/Title':'SegmentGDA | ACM Multimedia 2026 | A0 portrait','/Author':'Yiqi Wu; Huachao Wu; Ronglei Hu; Dejun Zhang'})
with open(OUT/'SegmentGDA_ACMMM2026_A0_v4.pdf','wb') as f:final.write(f)
print('Created A0 PDF and editable SVG.')
