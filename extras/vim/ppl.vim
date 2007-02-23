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
" Set command
syn match pplCommand /\v^\s*<set=>/ nextgroup=pplSetCommand skipwhite
syn match pplSetCommand /\v.*/ contained contains=pplSetTerm,pplTerminals 
syn match pplSetTerm /\v<t(e(r(m(i(n(al=)=)=)=)=)=)=>/ contained 
syn match pplTerminals /\v\s*<x(1(1(_(singlewindow)=)=)=)=>/ contained

highlight link pplSetTerm Type
highlight link pplTerminals Define
"(i(n(g(l(e(w(i(n(d(ow=)=)=)=)=)=)=)=)=)=)=)=)=)=)>/ contained


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Plot command (nothing like doing the hard bit first, eh?)
syn match pplCommand /\v^\s*<p(l(ot=)=)=>/ nextgroup=pplPlotCommand skipwhite
syn match pplPlotCommand /\v.{-}(<w(i(th=)=)=>|$)/ contained contains=pplUsing,pplSelect,pplTitle,pplEvery,pplIndex,pplSpecial,pplFloat,pplNumber,pplString,pplWith nextgroup=pplWithCommand
" Note that {-} matches the previous atoms 0+ times non-greedily (c.f. ?)
highlight link pplCommand Keyword

"using
syn match pplUsing /\v<u(s(i(ng=)=)=)=(\s+<colum(ns=)=>)=/ contained
syn match pplUsing /\v<u(s(i(ng=)=)=)=>\s+<(r(o(ws=)=)=|c(o(lu=)=)=)>/ contained
"(o(l(u(m(ns=)=)=)=)=)
highlight link pplUsing Type

"with
syn match pplWith /\v<w(i(th=)=)=>/ contained "contains=pplWithMods contained
highlight link pplWith Type
syn match pplWithCommand /.*$/ contained contains=pplWithMods,pplNumber
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
syn match pplSpecial /\m\[/ contained
syn match pplSpecial /\m\]/ contained
syn match pplSpecial /\m\:/ contained
syn match pplSpecial /\v\$[0-9]+/ contained
highlight link pplSpecial Special

" Numbers
syn match pplNumber /\<[0-9]*\>/ contained
highlight link pplNumber Number
syn match pplFloat          "[+-]\=\d\+\." contained
syn match pplFloat          "[+-]\=\d\+\.\d*\(e[+-]\=\d\+\)\=" contained
syn match pplFloat          "[+-]\=\.\d\+\(e[+-]\=\d\+\)\=" contained
syn match pplFloat          "[+-]\=\d\+e[+-]\=\d\+" contained
highlight link pplFloat Float

" Strings
syn region pplString start=/"/ skip=/\\"/ end=/"/ contained
syn region pplString start=/'/ skip=/\\'/ end=/'/ contained
highlight link pplString String

" Comments
syn match pplComment /#.*$/
highlight link pplComment Comment
