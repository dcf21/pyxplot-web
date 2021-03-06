" Vim syntax file
" Language: PyXPlot v0.6.x
" Maintainer: Ross Church (rpc25-pyxplot@srcf.ucam.org)
" Filenames: *.ppl
" 

" It is useful to note that vim appears to parse this file bottom upwards
" That is, things that you want to match first should be lower down.

" Clear syntax details
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

" ppl is largely case insensitive
syn case ignore

" Command keywords
"syn keyword pplKeyword fit set show spline
" Set command (Of which there is lots.  And lots.  And lots :-)
syn match pplCommand /\v^\s*<set=>/ skipwhite nextgroup=pplSetTerm,pplSetLabel,pplSetRange,pplSetTicdir,pplSetTics,pplSetArrow,pplSetAutoscale,pplSetAxescolour,pplSetAxis,pplSetBackup,pplSetBar,pplSetBoxfrom,pplSetBoxwidth,pplSetDatastyle,pplSetDisplay,pplSetDpi,pplSetFontsize,pplSetGrid,pplSetGrc,pplSetKey,pplSetKeyColumns,pplSetLinestyle,pplSetLinewidth,pplSetLog,pplSetMultiplot,pplSetNoarrow,pplSetNoaxis,pplSetNobackup,pplSetNodisplay,pplSetNogrid,pplSetNolabel,pplSetNols,pplSetNolog,pplSetNomult,pplSetNoxtics,pplSetNotitle,pplSetOr,pplSetOut,pplSetPal,pplSetPaper,pplSetPlw,pplSetPs,pplSetPreamble,pplSetSamp,pplSetSize,pplSetTextcol,pplSetTextH,pplSetTextV,pplSetTitle,pplSetWid
syn match pplSetWid /\v<w(i(d(th=)=)=)=>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetWid Type
syn match pplSetTitle /\v<ti(t(le=)=)=>/ contained nextgroup=pplQstring skipwhite
highlight link pplSetTitle Type
syn match pplSetTextH /\v<texth(a(l(i(gn=)=)=)=)=>/ contained nextgroup=pplTextH skipwhite
highlight link pplSetTextH Type
syn match pplTextH /\v<l(e(ft=)=)=>/ contained
syn match pplTextH /\v<c(e(n(t(re=)=)=)=)=>/ contained
syn match pplTextH /\v<c(e(n(t(er=)=)=)=)=>/ contained
syn match pplTextH /\vr(i(g(ht=)=)=)=>/ contained
highlight link pplTextH Define
syn match pplSetTextV /\v<textv(a(l(i(gn=)=)=)=)=>/ contained nextgroup=pplTextV skipwhite
highlight link pplSetTextV Type
syn match pplTextV /\v<t(op=)=>/ contained
syn match pplTextV /\v<c(e(n(t(re=)=)=)=)=>/ contained
syn match pplTextV /\v<c(e(n(t(er=)=)=)=)=>/ contained
syn match pplTextV /\v<b(o(t(t(o(m=)=)=)=)=)=>/ contained
highlight link pplTextV Define
syn match pplSetTextcol /\v<textc(o(l(ou=r=)=)=)=>/ contained nextgroup=pplString skipwhite
highlight link pplSetTextcol Type
syn match pplSetSize /\v<s(i(ze=)=)=>/ contained nextgroup=pplNumber,pplFloat,pplSize skipwhite
highlight link pplSetSize Type
syn match pplSize /\v<r(a(t(io=)=)=)=>/ contained nextgroup=pplNumber,pplFloat skipwhite
syn match pplSize /\v<n(o(r(a(t(io=)=)=)=)=)=>/ contained skipwhite
syn match pplSize /\v<s(q(u(a(re=)=)=)=)=>/ contained skipwhite
highlight link pplSize Define
syn match pplSetSamp /\v<sa(m(p(l(es=)=)=)=)=>/ contained nextgroup=pplNumber skipwhite
highlight link pplSetSamp Type
syn match pplSetPreamble /\v<pr(e(a(m(b(le=)=)=)=)=)=/ contained nextgroup=pplAnything skipwhite
highlight link pplSetPreamble Type
syn match pplSetPs /\v<(p(o(i(n(t(s(i(ze=)=)=)=)=)=)=)=|ps)>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetPs Type
syn match pplSetPlw /\v<(pointl(i(n(e(w(i(d(th=)=)=)=)=)=)=)=|plw)>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetPlw Type
syn match pplSetPaper /\v<pap(e(r(s(i(ze=)=)=)=)=)=>/ contained nextgroup=pplCoordinate,pplString,pplQstring skipwhite
highlight link pplSetPaper Type
syn match pplSetPal /\v<p(a(l(e(t(te=)=)=)=)=)=>/ contained nextgroup=pplCommalist skipwhite
highlight link pplSetPal Type
syn match pplSetOut /\v<o(u(t(p(ut=)=)=)=)=>/ contained nextgroup=pplString,pplQstring skipwhite
highlight link pplSetOut Type
syn match pplSetOr /\v<or(i(g(in=)=)=)=>/ contained nextgroup=pplCoordinate skipwhite
highlight link pplSetOr Type
syn match pplSetNotitle /\v<not(i(t(le=)=)=)=>/ contained
highlight link pplSetNotitle Type
syn match pplSetNoxtics /\v<nom?[xy][0-9]*tics>/ contained
highlight link pplSetNoxtics Type
syn match pplSetNomult /\v<nom(u(l(t(i(p(l(ot=)=)=)=)=)=)=)=>/ contained
highlight link pplSetNomult Type
syn match pplSetNolog /\v<nolo(g(s(c(a(le=)=)=)=)=)=>/ contained nextgroup=pplAxis skipwhite
highlight link pplSetNolog Type
syn match pplSetNols /\v<nol(i(n(e(s(t(y(le=)=)=)=)=)=)=)=>/ contained nextgroup=pplIntlist skipwhite
highlight link pplSetNols Type
syn match pplSetNolabel /\v<nola(b(el=)=)=>/ contained nextgroup=pplIntlist skipwhite
highlight link pplSetNolabel Type
syn match pplSetNogrid /\v<nog(r(id=)=)=>/ contained nextgroup=pplAxis
highlight link pplSetNogrid Type
syn match pplSetNodisplay /\v<nod(i(s(p(l(ay=)=)=)=)=)=>/ contained
highlight link pplSetNodisplay Type
syn match pplSetNobackup /\v<nob(a(c(k(up=)=)=)=)=>/ contained
highlight link pplSetNobackup Type
syn match pplSetNoaxis /\v<noa(x(is=)=)=>/ contained nextgroup=pplAxis skipwhite
highlight link pplSetNoaxis Type
syn match pplSetNoarrow /\v<noa(r(r(ow=)=)=)=>/ contained nextgroup=pplIntlist skipwhite
highlight link pplSetNoarrow Type
syn match pplSetMultiplot /\v<m(u(l(t(i(p(l(ot=)=)=)=)=)=)=)=>/ contained
highlight link pplSetMultiplot Type
syn match pplSetLog /\v<l(o(g(s(c(a(le=)=)=)=)=)=)=>/ contained nextgroup=pplAxis skipwhite
highlight link pplSetLog Type
syn match pplSetLinewidth /\v<linew(i(d(th=)=)=)=>/ contained nextgroup=pplNumber,pplFloat skipwhite 
syn match pplSetLinewidth /\v<lw>/ contained nextgroup=pplNumber,pplFloat skipwhite 
highlight link pplSetLinewidth Type
syn match pplSetLinestyle /\v<l(i(n(e(s(t(y(le=)=)=)=)=)=)=)=>\s*\d+/ contained contains=pplNumber nextgroup=pplWithCommand skipwhite
syn match pplSetLinestyle /\v<ls>\s*\d+/ contained contains=pplNumber nextgroup=pplWithCommand skipwhite
highlight link pplSetLinestyle Type
syn match pplSetLabel /\v<la(b(el=)=)=>\s+\d+/ contained contains=pplNumber nextgroup=pplSetLabelCommand skipwhite
syn match pplSetLabelCommand /.*/ contained contains=pplNumber,pplFloat,pplQstring,pplSetLabelMods
syn match pplSetLabelMods /\v<f(i(r(st=)=)=)=>/ contained
syn match pplSetLabelMods /\v<s(e(c(o(nd=)=)=)=)=>/ contained
syn match pplSetLabelMods /\v<sc(r(e(en=)=)=)=>/ contained
syn match pplSetLabelMods /\v<g(r(a(ph=)=)=)=>/ contained
syn match pplSetLabelMods /\v<axis>/ contained
syn match pplSetLabelMods /\v<at=>/ contained
syn match pplSetLabelMods /\v<r(o(t(a(te=)=)=)=)=>/ contained
highlight link pplSetLabelMods Define
syn match pplSetKeycolumns /\v<keyc(o(l(u(m(ns=)=)=)=)=)=>/ contained nextgroup=pplNumber skipwhite
highlight link pplSetKeyColumns Type
syn match pplSetKey /\v<k(ey=)=>/ contained nextgroup=pplSetKeyCommand skipwhite
syn match pplSetKeyCommand /.*/ contained contains=pplSetKeyMods,pplNumber,pplFloat
syn match pplSetKeyMods /\v<be(l(ow=)=)=>/ contained
syn match pplSetKeyMods /\v<o(u(t(s(i(de=)=)=)=)=)=>/ contained
syn match pplSetKeyMods /\v<l(e(ft=)=)=>/ contained
syn match pplSetKeyMods /\v<r(i(g(ht=)=)=)=>/ contained
syn match pplSetKeyMods /\v<[xy](c(e(n(t[re]{0,2})=)=)=)=>/ contained
syn match pplSetKeyMods /\v<t(op=)=>/ contained
syn match pplSetKeyMods /\v<bo(t(t(om=)=)=)=>/ contained
highlight link pplSetKey Type
highlight link pplSetKeyMods Define
syn match pplSetGrc /\v<gridm(aj=|in=)>/ contained nextgroup=pplColour skipwhite
syn match pplSetGrc /\v<gridm(aj|in)c(o(l(ou=r=)=)=)=>/ contained nextgroup=pplColour skipwhite
highlight link pplSetGrc Type
"highlight link pplSetGrc Type
syn match pplSetGrid /\v<g(r(id=)=)=>/ contained nextgroup=pplAxis skipwhite
syn match pplSetFontsize /\v<f(ou=(n(t(s(i(ze=)=)=)=)=)=)=/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetFontsize Type
syn match pplSetDpi /\v<dpi>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetDpi Type
syn match pplSetDisplay /\v<d(i(s(p(l(ay=)=)=)=)=)=>/ contained
highlight link pplSetDisplay Type
syn match pplSetDatastyle /\v<s(t(y(le=)=)=)=>\s*<d(a(ta=)=)=>/ contained nextgroup=pplWithCommand skipwhite " ph34r!
syn match pplSetDatastyle /\v<s(t(y(le=)=)=)=>\s*<f(u(n(c(t(i(on=)=)=)=)=)=)=>/ contained nextgroup=pplWithCommand skipwhite
syn match pplSetDatastyle /\v<d(a(ta=)=)=>\s*<s(t(y(le=)=)=)=>/ contained nextgroup=pplWithCommand skipwhite
syn match pplSetDatastyle /\v<f(u(n(c(t(i(on=)=)=)=)=)=)=>\s*<s(t(y(le=)=)=)=>/ contained nextgroup=pplWithCommand skipwhite
highlight link pplSetDatastyle Type
syn match pplSetBoxwidth /\v<b(o(x(w(i(d(th=)=)=)=)=)=)=>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetBoxwidth Type
syn match pplSetBoxfrom /\v<boxf(r(om=)=)=>/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetBoxFrom Type
syn match pplSetBar /\v<bar=>/ contained nextgroup=pplSetBarMods skipwhite
syn match pplSetBarMods /\v(l(a(r(ge=)=)=)=$|s(m(a(ll=)=)=)=$|[0-9\.]@=)/ contained nextgroup=pplNumber,pplFloat skipwhite
highlight link pplSetBar Type
highlight link pplSetBarMods Define
syn match pplSetBackup /\v<b(a(c(k(up=)=)=)=)=>/ contained
highlight link pplSetBackup Type
syn match pplSetAxis /\v<a(x(is=)=)=>/ contained nextgroup=pplAxis skipwhite
highlight link pplSetAxis Type
syn match pplSetAxescolour /\v<axesc(o(l(ou=r=)=)=)=>/ contained nextgroup=pplColour skipwhite
syn match pplColour /\v<\w+>/ contained skipwhite
highlight link pplSetAxescolour Type
highligh link pplColour Define
syn match pplSetAutoscale /\v<au(t(o(s(c(a(le=)=)=)=)=)=)=>/ contained nextgroup=pplAxis skipwhite
syn match pplAxis /\v([xy][0-9]+)+/ contained
highlight link pplSetAutoscale Type
highlight link pplAxis Define
syn match pplSetArrow /\v<a(r(r(ow=)=)=)=>/ contained nextgroup=pplSetArrowCommand skipwhite
syn match pplSetArrowCommand /\v(<f(r(om=)=)=>)=.*<to>.{-}((w(i(th=)=)=)@=|$)/ contained contains=pplSetArrowMods,pplNumber,pplFloat nextgroup=pplSetArrowWith skipwhite
syn match pplSetArrowMods /\v<f(r(om=)=)=>/ contained
syn match pplSetArrowMods /\v<f(i(r(st=)=)=)=>/ contained
syn match pplSetArrowMods /\v<s(e(c(o(nd=)=)=)=)=>/ contained
syn match pplSetArrowMods /\v<sc(r(e(en=)=)=)=>/ contained
syn match pplSetArrowMods /\v<g(r(a(ph=)=)=)=>/ contained
syn match pplSetArrowMods /\v<axis>/ contained
syn match pplSetArrowMods /\v<to>/ contained
"syn match pplSetArrowMods /\v<>/ contained
syn match pplSetArrowWith /\v<w(i(th=)=)=>/ contained nextgroup=pplSetArrowWithCommand skipwhite
syn match pplSetArrowWithCommand /.*/ contained contains=pplSetArrowWithMods,pplNumber
syn match pplSetArrowWithMods /\v<linet(y(pe=)=)=>/ contained
syn match pplSetArrowWithMods /\v<lt>/ contained
syn match pplSetArrowWithMods /\v<linew(i(d(th=)=)=)=>/ contained
syn match pplSetArrowWithMods /\v<lw>/ contained
syn match pplSetArrowWithMods /\v<linest(y(le=)=)=/ contained
syn match pplSetArrowWithMods /\v<ls>/ contained
syn match pplSetArrowWithMods /\v<c(o(l(ou=r=)=)=)=>/ contained
syn match pplSetArrowWithMods /\v<tw(o(h(e(ad=)=)=)=)=>/ contained
syn match pplSetArrowWithMods /\v<he(ad=)=>/ contained
syn match pplSetArrowWithMods /\v<tw(o(w(ay=)=)=)=>/ contained
syn match pplSetArrowWithMods /\v<no(h(e(ad=)=)=)=>/ contained
highlight link pplSetArrowWithMods Define
highlight link pplSetArrowWith Type
highlight link pplSetArrowMods Define
highlight link pplSetArrow Type
syn match pplSetTics /\v<m=[xy]=t(i(cs=)=)=>/ nextgroup=pplSetTicsCommand skipwhite
syn match pplSetTicsCommand /\v\s*(<\w*>)=/ contains=pplSetTicdirMods,pplSetTicMods nextgroup=pplSetTicMods contained skipwhite
syn match pplSetTicMods /\v[0-9\.e+-]+(\s*,\s*[0-9\.e+-]+(\s*,\s*[0-9\.e+-]+)=)=/ contained contains=pplFloat,pplNumber
syn match pplSetTicMods /\v\('[^']*'\s+[0-9\.e+-]+(\s*,\s*'[^']*'\s+[0-9\.e+-]+)*\)/ contained contains=pplQstring,pplFloat,pplNumber
syn match pplSetTicMods /\v\("[^"]*"\s+[0-9\.e+-]+(,\s*"[^"]*"\s+[0-9\.e+-]+)*\)/ contained contains=pplQstring,pplFloat,pplNumber
syn match pplSetTicMods /\v\s*<a(u(t(o(f(r(eq=)=)=)=)=)=)=>/ contained
highlight link pplSetTics Type
highlight link pplSetTicMods Define
syn match pplSetTicdir /\v<[xy][0-9]*ticd(ir=)=>/ nextgroup=pplSetTicdirMods contained skipwhite
syn match pplSetTicdirMods /\v<i(n(w(a(rd=)=)=)=)=/ contained
syn match pplSetTicdirMods /\v<o(u(t(w(a(rd=)=)=)=)=)=>/ contained
syn match pplSetTicdirMods /\v<b(o(th=)=)=>/ contained
highlight link pplSetTicdir Type
highlight link pplSetTicdirMods Define
syn match pplSetTerm /\v<t(e(r(m(i(n(al=)=)=)=)=)=)=>.*/ contained contains=pplTerminals 
syn match pplTerminals /\v<x(1(1(_(s(i(n(g(l(ewindow)=)=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<x11_single(w(i(n(d(ow=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<x11_m(u(l(t(i(w(i(n(d(ow=)=)=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<x11_p(e(r(s(i(st=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<p(o(s(t(s(c(r(i(pt=)=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<ps>/ contained
syn match pplTerminals /\v<e(ps=)=>/ contained
syn match pplTerminals /\v<pdf=>/ contained
syn match pplTerminals /\v<png=>/ contained
syn match pplTerminals /\v<g(if=)=>/ contained
syn match pplTerminals /\v<j(pe=g=)=>/ contained
syn match pplTerminals /\v<c(o(l(ou=r=)=)=)=>/ contained
syn match pplTerminals /\v<m(o(n(o(c(h(r(o(me=)=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<(no)=e(n(l(a(r(ge=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<l(a(n(d(s(c(a(pe=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<po(r(t(r(a(it=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<t(r(a(n(s(p(a(r(e(nt=)=)=)=)=)=)=)=)=)=>/ contained
syn match pplTerminals /\v<s(o(l(id=)=)=)=>/ contained
syn match pplTerminals /\v<(no)=i(n(v(e(rt=)=)=)=)=>/ contained
syn match pplTerminals /\v<no=>/ contained
highlight link pplSetTerm Type
highlight link pplTerminals Define
syn match pplSetLabel /\v<(x|y)[0-9]*l(a(b(el=)=)=)=>/ contained nextgroup=pplQstring skipwhite
highlight link pplSetLabel Type
syn match pplSetRange /\v<[xy][0-9]*r(a(n(ge=)=)=)=>/ contained nextgroup=pplRange skipwhite
highlight link pplSetRange Type
"syn match 


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Plot command (nothing like doing the hard bit first, eh?)
syn match pplCommand /\v^\s*<p(l(ot=)=)=>/ nextgroup=pplPlotCommand skipwhite
syn match pplPlotCommand /\v.{-}(<w(i(th=)=)=>|$)/ contained contains=pplUsing,pplSelect,pplTitle,pplEvery,pplIndex,pplRange,pplQstring,pplWith nextgroup=pplWithCommand
" Note that {-} matches the previous atoms 0+ times non-greedily (c.f. ?)
highlight link pplCommand Keyword
syn match pplPlotCommandGlue /,/ contained nextgroup=pplPlotCommand skipwhite

"using
syn match pplUsing /\v<u(s(i(ng=)=)=)=(\s+<colum(ns=)=>)=/ contained
syn match pplUsing /\v<u(s(i(ng=)=)=)=>\s+<(r(o(ws=)=)=|c(o(lu=)=)=)>/ contained
"(o(l(u(m(ns=)=)=)=)=)
highlight link pplUsing Type

"with
syn match pplWith /\v<w(i(th=)=)=>/ contained "contains=pplWithMods contained
highlight link pplWith Type
syn match pplWithCommand /\v[^,]+/ contained contains=pplWithMods,pplNumber nextgroup=pplPlotCommandGlue skipwhite
" Acceptable with keywords (glragghhh)
" Plotting styles
syn match pplWithMods /\v<p(o(i(n(ts=)=)=)=)=>/ contained
syn match pplWithMods /\v<l(i(n(es=)=)=)=>/ contained
syn match pplWithMods /\v<linesp(o(i(n(ts=)=)=)=)=>/ contained
syn match pplWithMods /\v<lp>/ contained
syn match pplWithMods /\v<b(o(x(es=)=)=)=>/ contained
syn match pplWithMods /\v<wb(o(x(es=)=)=)=>/ contained
syn match pplWithMods /\v<i(m(p(u(l(s(es=)=)=)=)=)=)>/ contained
syn match pplWithMods /\v<s(t(e(ps=)=)=)=>/ contained
syn match pplWithMods /\v<f(s(t(e(ps=)=)=)=)=>/ contained
syn match pplWithMods /\v<h(i(s(t(e(ps=)=)=)=)=)>/ contained
syn match pplWithMods /\v<e(r(r(o(r(b(a(rs=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<xe(r(r(o(r(b(a(rs=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<ye(r(r(o(r(b(a(rs=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<xye(r(r(o(r(b(a(rs=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<errorr(a(n(ge=)=)=)=>/ contained
syn match pplWithMods /\v<xerrorr(a(n(ge=)=)=)=>/ contained
syn match pplWithMods /\v<yerrorr(a(n(ge=)=)=)=>/ contained
syn match pplWithMods /\v<xyerrorr(a(n(ge=)=)=)=>/ contained
syn match pplWithMods /\v<arr(o(ws=)=)=>/ contained
syn match pplWithMods /\v<arr(o(w(s(_(h(e(ad=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<arr(o(w(s(_(h(e(ad=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<arr(o(w(s(_(n(o(h(e(ad=)=)=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<arr(o(w(s(_(t(w(o(w(ay=)=)=)=)=)=)=)=)=)=>/ contained
" Too many ( my arse.  Piece of shit, you are. :-)
syn match pplWithMods /\v<arr(o(w(s(_(t(w(o(h(ea=)=)=)=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<arrows_twohead>/ contained
syn match pplWithMods /\v<a=csp(l(i(n(es=)=)=)=)=>/ contained
" Other with modifiers
syn match pplWithMods /\v<linet(y(pe=)=)=>/ contained
syn match pplWithMods /\v<lt>/ contained
syn match pplWithMods /\v<linew(i(d(th=)=)=)=>/ contained
syn match pplWithMods /\v<lw>/ contained
syn match pplWithMods /\v<pointsi(ze=)=>/ contained
syn match pplWithMods /\v<ps>/ contained
syn match pplWithMods /\v<pointt(y(pe=)=)=/ contained
syn match pplWithMods /\v<pt>/ contained
syn match pplWithMods /\v<linest(y(le=)=)=/ contained
syn match pplWithMods /\v<ls>/ contained
syn match pplWithMods /\v<pointl(i(n(e(w(i(d(th=)=)=)=)=)=)=)>/ contained
syn match pplWithMods /\v<plw>/ contained
syn match pplWithMods /\v<fi(l(l(c(o(l(ou=r=)=)=)=)=)=)=>/ contained
syn match pplWithMods /\v<fc>/ contained
syn match pplWithMods /\v<c(o(l(ou=r=)=)=)=>/ contained
"syn match pplWithMods /\v<>/ contained
highlight link pplWithMods Define

" select
syn match pplSelect /\v<sel(e(ct=)=)>/ contained
highlight link pplSelect Type

" title
syn match pplTitle /\v<t(i(t(le=)=)=)=>/ contained
highlight link pplTitle Type

" every
syn match pplEvery /\v<e(v(e(ry=)=)=)=>/ contained
highlight link pplEvery Type

" index
syn match pplIndex /\v<i(n(d(ex=)=)=)=>/ contained
highlight link pplIndex Type

" Ranges
syn match pplRange /\v\[-=\d*\.=\d*(e[+-]=\d+)=:-=\d*\.=\d*(e[+-]=\d+)=\]/ contained
syn match pplRange /\V[]/ contained
syn match pplSpecial /\m\[/ contained
syn match pplSpecial /\m\]/ contained
syn match pplSpecial /\m\:/ contained
syn match pplSpecial /\v\$[0-9]+/ contained
highlight link pplRange Special

" Numbers
syn match pplIntlist /\v\d+(\s*,\s*\d+)*/ contained contains=pplNumber
syn match pplNumber /\<[0-9]*\>/ contained
highlight link pplNumber Number
syn match pplFloat          "[+-]\=\d\+\." contained
syn match pplFloat          "[+-]\=\d\+\.\d*\(e[+-]\=\d\+\)\=" contained
syn match pplFloat          "[+-]\=\.\d\+\(e[+-]\=\d\+\)\=" contained
syn match pplFloat          "[+-]\=\d\+e[+-]\=\d\+" contained
highlight link pplFloat Float

" Strings
syn region pplQstring start=/"/ skip=/\\"/ end=/"/ contained oneline
syn region pplQstring start=/'/ skip=/\\'/ end=/'/ contained oneline
highlight link pplQstring String
syn match pplString /\v[a-zA-Z0-9]+/ contained
highlight link pplString String

" Comma separated list of strings
syn match pplCommalist /\v'=[a-z0-9A-Z]+'=(\s*,\s*'=[a-z0-9A-Z]+'=)*\s*$/ contained contains=pplString,pplQstring

" Co-ordinates
syn match pplCoordinate /\v<[0-9\.eE]+, *[0-9\.eE]+/ contained contains=pplNumber,pplFloat

" Comments
syn match pplComment /#.*$/
highlight link pplComment Comment

" Anything
syn match pplAnything /.*$/ contained
highlight link pplAnything Comment
