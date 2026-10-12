import subprocess,re,sys,html
pdf=sys.argv[1]; first=int(sys.argv[2]) if len(sys.argv)>2 else 5
x=subprocess.run(['pdftotext','-bbox-layout',pdf,'-'],capture_output=True,text=True).stdout
pages=x.split('<page ')[1:]
issues=[]
for pn,pg in enumerate(pages,1):
    if pn<first: continue
    lines=[]
    for ln in re.findall(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',pg,re.S):
        x0,y0,x1,y1,body=ln; words=re.findall(r'>([^<]*)</word>',body)
        lines.append((float(x0),float(y0),float(x1),html.unescape(' '.join(words))))
    lines=[l for l in lines if not re.fullmatch(r'\d+',l[3].strip())]  # drop folio
    if len(lines)<6: continue
    L=min(l[0] for l in lines); R=max(l[2] for l in lines)
    top=lines[0]; bot=lines[-1]
    if top[0]-L<4 and (R-top[2])>(R-L)*0.45 and not top[3].startswith(('“','*')):
        issues.append((pn,'WIDOW (1 line at top)',top[3][:50]))
    if (bot[0]-L)>8 and (R-bot[2])<6:
        issues.append((pn,'ORPHAN (1st line at foot)',bot[3][:50]))
for i in issues: print(*i)
print(len(issues),'issues /',len(pages),'pages')
