import type {ReactNode} from 'react';
export function Panel({title,children,tag}:{title:string;children:ReactNode;tag?:string}){return <section className="panel"><h2>{title}{tag&&<em>{tag}</em>}</h2>{children}</section>}
