from pathlib import Path
import base64,html,io,json,shutil
import pymupdf as fitz
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import qr

ROOT=Path(__file__).resolve().parents[2]
TMP=ROOT/'tmp'/'final-poster'
OUT=ROOT/'output'/'final'
ASSETS=Path(__file__).resolve().parent/'assets'
TMP.mkdir(parents=True,exist_ok=True)
OUT.mkdir(parents=True,exist_ok=True)
W,H=1682,2378;S=72/25.4/2
BLACK='#17202B';SECONDARY='#344256';BLUE='#173FA2';ORANGE='#A8401B';PALE='#EDF2FC';RULE='#A6B0BD'
FONT_WEIGHTS={'R':400,'M':500,'S':600,'B':700,'X':800}
for name,weight in FONT_WEIGHTS.items():pdfmetrics.registerFont(TTFont(name,str(ASSETS/'fonts'/f'Inter-{weight}.ttf')))
PDF=OUT/'SegmentGDA_ACMMM2026_A0_final.pdf'
C=canvas.Canvas(str(PDF),pagesize=(W*S,H*S),pageCompression=1)
C.setTitle('SegmentGDA | ACM Multimedia 2026 | A0 Portrait')
C.setAuthor('Yiqi Wu, Huachao Wu, Ronglei Hu, Dejun Zhang')
C.setSubject('Training-Free Few-Shot Segmentation via Gaussian Discriminant Analysis on Vision Foundation Features')
C.scale(S,S);SVG=[];TEXT=[];IMAGES=[]
def rect(x,y,w,h,fill='#FFFFFF',stroke=None,sw=1):
 C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(stroke or fill));C.setLineWidth(sw)
 C.rect(x,H-y-h,w,h,fill=1,stroke=int(bool(stroke)))
 SVG.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw}"/>')
def line(x,y,xx,yy,color=RULE,sw=1):
 C.setStrokeColor(HexColor(color));C.setLineWidth(sw);C.line(x,H-y,xx,H-yy)
 SVG.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="{color}" stroke-width="{sw}"/>')
def text(x,y,t,size=22,font='R',color=BLACK,align='left',maxw=None,bg='#FFFFFF'):
 width=pdfmetrics.stringWidth(t,font,size)
 if maxw:assert width<=maxw+.2,(t,width,maxw)
 xx=x-(width/2 if align=='center' else width if align=='right' else 0)
 assert xx>=0 and xx+width<=W and y>=0 and y+size<=H,(t,xx,y,width,size)
 C.setFillColor(HexColor(color));C.setFont(font,size);C.drawString(xx,H-y-size*.82,t)
 SVG.append(f'<text x="{xx}" y="{y+size*.82}" font-family="Poster{font}" font-size="{size}" fill="{color}">{html.escape(t)}</text>')
 TEXT.append({'text':t,'x':xx,'top':y,'width':width,'size':size,'color':color,'background':bg})
def para(x,y,t,width,size=21,font='R',color=SECONDARY,leading=None):
 leading=leading or size*1.36;yy=y
 for paragraph in t.split('\n'):
  current=''
  for word in paragraph.split():
   candidate=(current+' '+word).strip()
   if pdfmetrics.stringWidth(candidate,font,size)>width and current:
    text(x,yy,current,size,font,color,maxw=width);yy+=leading;current=word
   else:current=candidate
  if current:text(x,yy,current,size,font,color,maxw=width);yy+=leading
 return yy
def image(im,x,y,w,h,source=None):
 C.drawImage(ImageReader(im),x,H-y-h,w,h,mask='auto')
 b=io.BytesIO();im.save(b,format='PNG')
 SVG.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}"/>')
 IMAGES.append({'source':source,'box':[x,y,w,h],'pixels':list(im.size)})
def qr_code(url,x,y,size):
 q=qr.QrCodeWidget(url,barLevel='M',barBorder=4);q.qr.make();n=q.qr.getModuleCount();u=size/(n+8)
 rect(x,y,size,size)
 for rr in range(n):
  for cc in range(n):
   if q.qr.isDark(rr,cc):rect(x+(cc+4)*u,y+(rr+4)*u,u+.02,u+.02,BLACK)
def section(title,y,size=36):
 text(76,y-5,title,size,'S',BLACK,maxw=1530)

def ribbon(x,y,w,title):
 rect(x,y,w,46,BLUE)
 rect(x,y,6,46,ORANGE)
 text(x+21,y+10,title,29,'S','#FFFFFF',maxw=w-42,bg=BLUE)

rect(0,0,W,H)
rect(0,0,W,8,BLUE)
text(76,33,'ACM MULTIMEDIA 2026',18,'B',BLUE)
text(1606,33,'RIO DE JANEIRO, BRAZIL  |  10-14 NOVEMBER 2026',17,'M',SECONDARY,'right')
line(76,67,1606,67,BLACK,1.4)
text(69,82,'Segment',118,'X',BLACK)
namex=69+pdfmetrics.stringWidth('Segment','X',118)
text(namex-2,82,'GDA',118,'X',BLUE)
rect(1090,90,516,93,ORANGE)
text(1348,117,'ACM MM 2026',38,'B','#FFFFFF','center',bg=ORANGE)
text(76,222,'Training-Free Few-Shot Segmentation via',32,'S',BLACK)
text(76,264,'Gaussian Discriminant Analysis on Vision Foundation Features',32,'S',BLACK,maxw=1240)
text(76,310,'Yiqi Wu*    Huachao Wu*    Ronglei Hu    Dejun Zhang†',23,'M',BLACK,maxw=1200)
text(76,346,'School of Computer Science, China University of Geosciences, Wuhan, China',20,'R',SECONDARY,maxw=1220)
qr_code('https://github.com/wavachao/SegmentGDA',1135,215,132)
qr_code('https://doi.org/10.1145/3767308.3835710',1450,215,132)
text(1201,357,'CODE',17,'B',BLUE,'center')
text(1516,357,'PAPER',17,'B',BLUE,'center')

ribbon(76,394,1530,'Method')
method=fitz.open(ASSETS/'method.pdf');mr=method[0].rect
METHOD=(76,454,1606,454+1530*mr.height/mr.width)
method_svg=(ASSETS/'method.svg').read_bytes()
SVG.append(f'<image x="76" y="454" width="1530" height="{METHOD[3]-METHOD[1]}" href="data:image/svg+xml;base64,{base64.b64encode(method_svg).decode()}"/>')
text(76,828,'Backbones: DINOv2 ViT-L/14 and SAM ViT-H (both frozen).',21,'R',SECONDARY,maxw=1530)

ribbon(76,880,1530,'Qualitative comparison')
paper=fitz.open(ROOT/'3767308.3835710.pdf')
blocks=[b for b in paper[5].get_text('dict')['blocks'] if b['type']==1]
comparisons=[Image.open(io.BytesIO(b['image'])).convert('RGB') for b in blocks]
values=[
 [[.26,.20,.51,.03,.47,.52,.95,.79],[.34,.64,.38,.55,.72,.24,.71,.92],[.93,.92,.71,.68,.85,.59,.97,.93]],
 [[.20,.31,.77,.10,.91,.70,.93,.90],[.96,.26,.81,.80,.39,.73,.91,.90],[.86,.86,.93,.87,.97,.77,.96,.92]]
]
tile_manifest=[]
starts=[184,910];pw=696;gap=2.5;cell=(pw-gap*7)/8
text(76,1026,'Method',18,'S',SECONDARY)
for ds,x,im,ious,fig in zip(['COCO-20ⁱ','FSS-1000'],starts,comparisons,values,[3,4]):
 text(x,950,ds,27,'S',BLACK)
 text(x,991,'5-shot | IoU (0-1)',20,'R',SECONDARY)
 for cc in range(8):text(x+cc*(cell+gap)+cell/2,1026,str(cc+1),17,'M',SECONDARY,'center')
 for rr in range(4):
  yy=1052+rr*110
  for cc in range(8):
   box=(round(cc*im.width/8),round(rr*im.height/4),round((cc+1)*im.width/8),round((rr+1)*im.height/4))
   xx=x+cc*(cell+gap)
   image(im.crop(box),xx,yy,cell,cell,source=f'Figure {fig}, row {rr+1}, episode {cc+1}')
   score=None if rr==0 else ious[rr-1][cc]
   if score is not None:text(xx+cell/2,yy+cell+4,f'{score:.2f}',18,'M',BLACK,'center')
   tile_manifest.append({'figure':fig,'row':rr,'episode':cc,'source_box':box,'iou':score})
for rr,parts in enumerate([['Ground','truth'],['Matcher'],['GF-SAM'],['Segment','GDA']]):
 yy=1052+rr*110
 if rr==3:rect(76,yy+4,4,cell-7,BLUE)
 for j,t in enumerate(parts):
  text(87 if rr==3 else 76,yy+cell/2-11+(j-(len(parts)-1)/2)*25,t,20,'S' if rr==3 else 'M',BLUE if rr==3 else BLACK,maxw=96 if rr==3 else 106)
line(76,1507,1606,1507,RULE,1)

# A compact table and legend occupy a single aligned band.
qx=76;qw=995;lx=1111;lw=495
ribbon(qx,1527,qw,'Benchmark results')
ribbon(lx,1527,lw,'Legend')
text(qx,1586,'Selected training-free baselines | 5-shot mIoU (%)',20,'R',SECONDARY,maxw=qw)
rect(qx,1615,qw,36,PALE)
text(qx+12,1622,'Method',21,'S',BLACK,bg=PALE)
centers=[425,610,795,980]
for xx,t in zip(centers,['COCO-20ⁱ','FSS-1000','LVIS-92ⁱ','PASCAL-5ⁱ']):text(xx,1622,t,21,'S',BLACK,'center',maxw=180,bg=PALE)
rows=[('Matcher',[60.7,89.6,40.0,74.0]),('UNICL-SAM',[78.7,86.3,37.4,None]),('GF-SAM',[66.8,88.9,44.2,82.6]),('SegmentGDA',[62.5,89.8,41.8,82.2])]
best=[78.7,89.8,44.2,82.6]
for rr,(name,nums) in enumerate(rows):
 yy=1653+rr*39;bg=PALE if rr==3 else '#FFFFFF'
 if rr==3:rect(qx,yy-1,qw,39,PALE)
 text(qx+12,yy+7,name,23,'S' if rr==3 else 'R',BLUE if rr==3 else BLACK,maxw=240,bg=bg)
 for col,v in enumerate(nums):text(centers[col],yy+7,'-' if v is None else f'{v:.1f}',24,'B' if v==best[col] else 'R',BLUE if rr==3 else BLACK,'center',bg=bg)
 line(qx,yy+38,qx+qw,yy+38,RULE,.7)
text(lx,1585,'Method comparison',20,'S',BLACK)
for j,(lab,col) in enumerate([('GT','#D6BE32'),('Matcher','#C93D46'),('GF-SAM','#4868AE'),('Ours','#2F966F')]):
 xx=lx+(j%2)*246;yy=1621+(j//2)*37
 rect(xx,yy,20,20,col,stroke=BLACK,sw=.6)
 text(xx+29,yy-1,lab,20,'M',BLACK,maxw=205)
text(lx,1702,'Posterior-guided masks',20,'S',BLACK)
text(lx,1736,'Prompts: green stars (+), red crosses (-).',19,'R',SECONDARY,maxw=lw)
text(lx,1767,'Masks: prediction (red), ground truth (green).',19,'R',SECONDARY,maxw=lw)
text(lx,1803,'Column best in bold; -: unreported.',18,'R',SECONDARY,maxw=lw)

# The inference examples form a full-width gallery: five groups, two by two each.
ribbon(76,1834,1530,'Posterior-guided segmentation  |  COCO-20ⁱ, 5-shot')
inf_block=[b for b in paper[7].get_text('dict')['blocks'] if b['type']==1][0]
inf=Image.open(io.BytesIO(inf_block['image'])).convert('RGB')
tile=142;inside=8;group=292;between=17.5
for episode in range(5):
 x=76+episode*(group+between)
 rect(x,1894,group,26,PALE)
 text(x+group/2,1898,str(episode+1),18,'S',BLUE,'center',bg=PALE)
 for role,lab in enumerate(['Query','Posterior','Prediction','Ground truth']):
  xx=x+(role%2)*(tile+inside);yy=1962 if role<2 else 2149
  text(xx+tile/2,1932 if role<2 else 2119,lab,19,'M',BLACK,'center',maxw=tile)
  box=(round(role*inf.width/4),round(episode*inf.height/5),round((role+1)*inf.width/4),round((episode+1)*inf.height/5))
  image(inf.crop(box),xx,yy,tile,tile,source=f'Figure 5, role {role+1}, episode {episode+1}')
  tile_manifest.append({'figure':5,'role':role,'episode':episode,'source_box':box})

line(76,2317,1606,2317,BLACK,1.4)
text(76,2337,'github.com/wavachao/SegmentGDA',20,'B',BLACK)
text(1606,2339,'* Equal contribution   † zhangdejun@cug.edu.cn',17,'R',SECONDARY,'right')
C.showPage();C.save()



doc=fitz.open(PDF);page=doc[0]
page.show_pdf_page(fitz.Rect(*[v*S for v in METHOD]),method,0,keep_proportion=True,overlay=True)
for box,url in [((1135,215,1267,347),'https://github.com/wavachao/SegmentGDA'),((1450,215,1582,347),'https://doi.org/10.1145/3767308.3835710'),((76,2337,760,2365),'https://github.com/wavachao/SegmentGDA')]:
 page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(*[v*S for v in box]),'uri':url})
doc.save(OUT/'final-linked.pdf',garbage=4,deflate=True);doc.close();(OUT/'final-linked.pdf').replace(PDF)

css=[]
for name,w in FONT_WEIGHTS.items():
 data=base64.b64encode((ASSETS/'fonts'/f'Inter-{w}.ttf').read_bytes()).decode()
 css.append(f"@font-face{{font-family:Poster{name};src:url(data:font/ttf;base64,{data}) format('truetype');}}")
svg='<svg xmlns="http://www.w3.org/2000/svg" width="841mm" height="1189mm" viewBox="0 0 1682 2378"><defs><style>'+''.join(css)+'</style></defs>'+''.join(SVG)+'</svg>'
(OUT/'SegmentGDA_ACMMM2026_A0_editable.svg').write_text(svg,encoding='utf-8')
assert len(tile_manifest)==84
assert sum('iou' in i and i['iou'] is not None for i in tile_manifest)==48
(TMP/'layout.json').write_text(json.dumps({'text':TEXT,'images':IMAGES,'tiles':tile_manifest,'method_box':METHOD},ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(ASSETS/'fonts'/'OFL.txt',OUT/'Inter-OFL.txt')
print('CREATED',PDF)
print('Scientific tiles:',len(tile_manifest),'Explicit IoU scores:',48,'Method aspect:',mr.width/mr.height)
