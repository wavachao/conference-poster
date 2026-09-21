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
    text(x,y,num,31,True,TEAL)
    text(x+23,y,title,34,True,NAVY)
    line(x,y+7,x+width,y+7,TEAL,0.8)

def raster(x,y,w,h,path):
    c.drawImage(str(path),x*MM,(H-y-h)*MM,w*MM,h*MM)
    data=base64.b64encode(path.read_bytes()).decode()
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/jpeg;base64,{data}"/>')

rect(0,0,W,H,WHITE)
rect(0,0,W,164,NAVY)
rect(26,20,21,2,'#57D0C1')
text(55,24,'ACM MULTIMEDIA 2026',26,True,'#A9E3DC')
text(815,24,'10-14 NOVEMBER 2026   /   RIO DE JANEIRO',22,False,WHITE,'end')
text(26,64,'SegmentGDA',94,True,WHITE)
text(27,89,'Training-Free Few-Shot Segmentation via',43,True,WHITE)
text(27,109,'Gaussian Discriminant Analysis on Vision Foundation Features',39,True,WHITE)
text(28,135,'Yiqi Wu*    Huachao Wu*    Ronglei Hu    Dejun Zhang',30,False,WHITE)
text(28,152,'School of Computer Science, China University of Geosciences, Wuhan, China',24,False,'#C8DFE3')

heading(26,188,'01','Motivation',377)
para(26,211,'Few-shot segmentation transfers a target concept from a few annotated support images to a new query.',377,29,leading=12)
para(26,249,'Local patch matching can miss object parts and confuse background clutter.',377,27,color=MUTED,leading=11)
heading(439,188,'02','Core idea',376)
para(439,212,'Model foreground and background as distributions in frozen foundation features.',376,31,True,leading=13)
para(439,251,'Use Bayesian posteriors to generate reliable SAM prompts, without task-specific training or fine-tuning.',376,27,color=MUTED,leading=11)

heading(26,293,'03','Method overview',789)
# The final PDF overlays the original vector diagram in this rectangle.
mx,my,mw = 26,320,550
mh=mw*(bottom-top)/(right-left)
method_svg=base64.b64encode((ASSETS/'method.svg').read_bytes()).decode()
svg.append(f'<image x="{mx}" y="{my}" width="{mw}" height="{mh}" xlink:href="data:image/svg+xml;base64,{method_svg}"/>')
text(603,326,'1  Frozen features',30,True,TEAL)
para(603,343,'DINOv2 ViT-L/14 extracts dense features. Apply a signed square-root transform and L2 normalization.',212,26,leading=11)
text(603,398,'2  Gaussian inference',30,True,TEAL)
para(603,415,'Estimate two class means and a shared, ridge-regularized covariance. Compute each query patch\'s foreground posterior.',212,26,leading=11)
text(603,481,'3  Posterior-guided SAM',28,True,TEAL)
para(603,498,'Sample spatially diverse positive and negative points. Refine errors iteratively with frozen SAM ViT-H.',212,26,leading=11)

heading(26,586,'04','Results across four benchmarks',488)
text(26,609,'Reported mIoU (%)    1-shot and 5-shot evaluation',25,False,MUTED)
tablex=[30,285,372,497]
rect(26,620,488,19,NAVY)
for x,s,a in zip(tablex,['Dataset','1-shot','5-shot','Gain (pp)'],['start','end','end','end']):text(x,633,s,25,True,WHITE,a)
rows=[('COCO-20i','42.1','62.5','+20.4'),('FSS-1000','82.9','89.8','+6.9'),('LVIS-92i','26.2','41.8','+15.6'),('PASCAL-5i','59.5','82.2','+22.7')]
for i,row in enumerate(rows):
    yy=639+i*22
    if i%2==0:rect(26,yy,488,22,PALE)
    for j,(x,s) in enumerate(zip(tablex,row)):text(x,yy+15,s,29,j==2,TEAL if j>=2 else INK,'start' if j==0 else 'end')
    line(26,yy+22,514,yy+22,RULE,0.3)
para(26,749,'PASCAL-5i, 5-shot: 82.2 vs. Matcher 74.0 and GF-SAM 82.6.',488,26,leading=11)
para(26,778,'Largest gains arise with more support images. One-shot estimates remain less reliable.',488,25,color=MUTED,leading=10)

heading(551,586,'05','Ablation',264)
text(551,609,'COCO-20i, 5-shot mIoU (%)',25,False,MUTED)
ab=[('Point-wise matching','53.6'),('Mean-only Euclidean','59.9'),('Shared diagonal covariance','60.8'),('Shared full covariance','62.5')]
for i,(label,value) in enumerate(ab):
    yy=638+i*25
    if i==3:rect(547,yy-14,268,22,PALE)
    text(551,yy,label,24,i==3)
    text(809,yy,value,29,True,TEAL if i==3 else INK,'end')
    line(551,yy+8,815,yy+8,RULE,0.3)
text(551,762,'+8.9 pp',55,True,TEAL)
para(551,782,'over point-wise matching in the controlled ablation.',264,25,color=MUTED,leading=10)

heading(26,835,'06','Qualitative comparisons',789)
text(26,861,'COCO-20i',29,True,NAVY)
text(435,861,'FSS-1000',29,True,NAVY)
raster(26,875,380,380*1030/2062,ASSETS/'qualitative_coco.jpg')
raster(435,875,380,380*1030/2062,ASSETS/'qualitative_fss.jpg')
text(26,1080,'Rows: ground truth / Matcher / GF-SAM / SegmentGDA. Selected 5-shot episodes from the paper.',24,False,MUTED)

rect(0,1101,W,88,PALE)
text(26,1122,'TAKEAWAY',25,True,TEAL)
para(26,1142,'Global feature statistics enable training-free mask transfer, with strong gains from additional support examples.',640,30,True,NAVY,12)
text(26,1175,'* Equal contribution.  Correspondence: zhangdejun@cug.edu.cn',21,False,MUTED)
text(745.5,1175,'SOURCE CODE',20,True,TEAL,'middle')

# A vector QR code remains sharp at print scale.
codeurl='https://github.com/wavachao/SegmentGDA'
widget=qr.QrCodeWidget(codeurl,barLevel='M'); widget.qr.make()
matrix=widget.qr.modules; n=len(matrix); unit=55/(n+8)
rect(718,1108,55,55,WHITE)
for row,cells in enumerate(matrix):
    for col,on in enumerate(cells):
        if on:rect(718+(col+4)*unit,1108+(row+4)*unit,unit,unit,NAVY)
c.linkURL(codeurl,(710*MM,(H-1180)*MM,809*MM,(H-1105)*MM),relative=0)
svg.append('</svg>')
(OUT/'SegmentGDA_ACMMM2026_A0_editable.svg').write_text('\n'.join(svg),encoding='utf-8')
c.showPage();c.save()

base=PdfReader(TMP/'poster_base.pdf').pages[0]
method=PdfReader(ASSETS/'method.pdf').pages[0]
scale=mw*MM/(right-left)
base.merge_transformed_page(method,Transformation().scale(scale).translate(mx*MM,(H-my-mh)*MM))
final=PdfWriter();final.add_page(base)
final.add_metadata({'/Title':'SegmentGDA | ACM Multimedia 2026 | A0 portrait','/Author':'Yiqi Wu; Huachao Wu; Ronglei Hu; Dejun Zhang'})
with open(OUT/'SegmentGDA_ACMMM2026_A0.pdf','wb') as f:final.write(f)
print('Created A0 PDF and editable SVG.')
