import{c as m,e as x,f as h,s as y,a as t,b as C,t as S,d as E}from"./index-BKXDy3Xv.js";import{f as L,l as p,s as q}from"./util_login_register-CgD28bB6.js";var P=S('<div class="w-[25rem] my-auto self-center"><div class="w-full my-7 font-semibold text-center text-4xl">Login</div><form><label><div>Email</div><input required type=email autocomplete=email></label><label><div>Password</div><input required type=password autocomplete=new-password></label><button type=submit>Login');function D(){const[i,b]=m(),[n,f]=m();return(()=>{var r=P(),g=r.firstChild,l=g.nextSibling,s=l.firstChild,c=s.firstChild,$=c.nextSibling,a=s.nextSibling,_=a.firstChild,v=_.nextSibling,d=a.nextSibling;return l.addEventListener("submit",e=>{e.preventDefault();const u=i(),o=n();u!=null&&o!=null&&x({email:u,password:o}).then(()=>{h().then(w=>{y(w)})})}),t(l,L),t(s,p),$.$$input=e=>{b(e.target.value)},t(a,p),v.$$input=e=>{f(e.target.value)},t(d,`${q} w-full px-4 py-2 rounded-lg bg-blue-700 disabled:bg-gray-400 text-white`),C(()=>d.disabled=i()==null||n()==null),r})()}E(["input"]);export{D as default};