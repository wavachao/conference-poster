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
NAVY, TEAL, INK, MUTED = '#123B46', '#007E80', '#17303B', '#536771'
PALE, RULE, WHITE = '#EAF4F3', '#C8D8DB', '#FFFFFF'
for name, filename in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
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
    font='Arial-Bold' if bold else 'Arial'
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
    svg.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size/MM}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{"".join(parts)}</text>')

def para(x,y,s,width,size=28,bold=False,color=INK,leading=12):
    font='Arial-Bold' if bold else 'Arial'
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
    text(x,y,num,36,True,TEAL)
    text(x+25,y,title,43,True,NAVY)
    line(x,y+8,x+width,y+8,TEAL,1)

def raster(x,y,w,h,path):
    c.drawImage(str(path),x*MM,(H-y-h)*MM,w*MM,h*MM)
    data=base64.b64encode(path.read_bytes()).decode()
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/jpeg;base64,{data}"/>')

rect(0,0,W,H,WHITE)
rect(0,0,W,164,NAVY)
rect(26,20,21,2,'#57D0C1')
text(55,24,'ACM MULTIMEDIA 2026',26,True,'#A9E3DC')
text(815,24,'10-14 NOVEMBER 2026   /   RIO DE JANEIRO',22,False,WHITE,'end')
text(420.5,64,'SegmentGDA: Training-Free Few-Shot Segmentation',72,True,WHITE,'middle')
text(420.5,96,'via Gaussian Discriminant Analysis on Vision Foundation Features',64,True,WHITE,'middle')
text(420.5,129,'Yiqi Wu*    Huachao Wu*    Ronglei Hu    Dejun Zhang',37,False,WHITE,'middle')
text(420.5,151,'School of Computer Science, China University of Geosciences, Wuhan, China',30,False,'#DFEDF0','middle')

heading(26,188,'01','Motivation',377)
para(26,213,'Segment a novel object from only a few annotated support examples.',377,36,leading=15)
para(26,253,'Local patch matching can miss object parts and select background clutter.',377,34,color=INK,leading=14)
heading(439,188,'02','Core idea',376)
para(439,213,'Model foreground and background as distributions in frozen foundation features.',376,36,True,leading=15)
para(439,265,'Bayesian posteriors guide SAM prompts. No task-specific training or fine-tuning.',376,33,color=INK,leading=14)

heading(26,311,'03','Method overview',789)
# The final PDF overlays the original vector diagram in this rectangle.
mx,my,mw = 26,331,570
mh=mw*(bottom-top)/(right-left)
method_svg=base64.b64encode((ASSETS/'method.svg').read_bytes()).decode()
svg.append(f'<image x="{mx}" y="{my}" width="{mw}" height="{mh}" xlink:href="data:image/svg+xml;base64,{method_svg}"/>')
text(619,345,'1  Frozen features',34,True,TEAL)
para(619,366,'DINOv2 ViT-L/14 features, signed square-root transform and L2 normalization.',196,32,leading=13.5)
text(619,429,'2  Gaussian inference',33,True,TEAL)
para(619,450,'Two class means and a shared covariance yield patch-level foreground posteriors.',196,32,leading=13.5)
text(619,519,'3  SAM refinement',34,True,TEAL)
para(619,540,'Diverse positive and negative points guide frozen SAM ViT-H to iteratively correct errors.',196,32,leading=13.5)

heading(26,612,'04','Benchmark results',488)
text(26,638,'mIoU (%)     Gain = 5-shot minus 1-shot',30,False,MUTED)
tablex=[30,285,372,497]
rect(26,649,488,22,NAVY)
for x,s,a in zip(tablex,['Dataset','1-shot','5-shot','Gain (pp)'],['start','end','end','end']):text(x,665,s,31,True,WHITE,a)
rows=[('COCO-20i','42.1','62.5','+20.4'),('FSS-1000','82.9','89.8','+6.9'),('LVIS-92i','26.2','41.8','+15.6'),('PASCAL-5i','59.5','82.2','+22.7')]
for i,row in enumerate(rows):
    yy=671+i*24
    if i%2==0:rect(26,yy,488,24,PALE)
    for j,(x,s) in enumerate(zip(tablex,row)):text(x,yy+17,s,36,j==2,TEAL if j>=2 else INK,'start' if j==0 else 'end')
    line(26,yy+24,514,yy+24,RULE,0.3)
para(26,793,'PASCAL-5i, 5-shot: 82.2 vs. Matcher 74.0 and GF-SAM 82.6.',488,32,leading=13)
para(26,831,'More support examples improve the estimates. One-shot performance remains a limitation.',488,31,color=INK,leading=13)

heading(551,612,'05','Ablation',264)
text(551,638,'COCO-20i, 5-shot mIoU (%)',30,False,MUTED)
ab=[('Point-wise matching','53.6'),('Mean-only Euclidean','59.9'),('Shared diagonal covariance','60.8'),('Shared full covariance','62.5')]
for i,(label,value) in enumerate(ab):
    yy=665+i*28
    if i==3:rect(547,yy-16,268,26,PALE)
    text(551,yy,label,30,i==3)
    text(809,yy,value,36,True,TEAL if i==3 else INK,'end')
    line(551,yy+8,815,yy+8,RULE,0.3)
text(551,803,'+8.9 pp',60,True,TEAL)
para(551,829,'over point-wise matching in the controlled ablation.',264,31,color=INK,leading=13)

heading(26,880,'06','Qualitative comparisons',789)
text(26,905,'COCO-20i',34,True,NAVY)
text(435,905,'FSS-1000',34,True,NAVY)
raster(26,916,380,380*1030/2062,ASSETS/'qualitative_coco.jpg')
raster(435,916,380,380*1030/2062,ASSETS/'qualitative_fss.jpg')
text(26,1121,'Rows: ground truth / Matcher / GF-SAM / SegmentGDA. Selected 5-shot episodes.',27,False,MUTED)

rect(0,1135,W,54,PALE)
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
(OUT/'SegmentGDA_ACMMM2026_A0_v2_editable.svg').write_text('\n'.join(svg),encoding='utf-8')
c.showPage();c.save()

base=PdfReader(TMP/'poster_base.pdf').pages[0]
method=PdfReader(ASSETS/'method.pdf').pages[0]
scale=mw*MM/(right-left)
base.merge_transformed_page(method,Transformation().scale(scale).translate(mx*MM,(H-my-mh)*MM))
final=PdfWriter();final.add_page(base)
final.add_metadata({'/Title':'SegmentGDA | ACM Multimedia 2026 | A0 portrait','/Author':'Yiqi Wu; Huachao Wu; Ronglei Hu; Dejun Zhang'})
with open(OUT/'SegmentGDA_ACMMM2026_A0_v2.pdf','wb') as f:final.write(f)
print('Created A0 PDF and editable SVG.')
