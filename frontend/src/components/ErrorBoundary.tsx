import {Component,type ErrorInfo,type ReactNode} from 'react';

type Props={label:string;children:ReactNode};
type State={failed:boolean};
export class ErrorBoundary extends Component<Props,State>{
  state:State={failed:false};
  static getDerivedStateFromError():State{return {failed:true};}
  componentDidCatch(_error:Error,_info:ErrorInfo){/* Deliberately do not expose implementation details to HMI users. */}
  render(){return this.state.failed?<section className="panel component-error"><h2>{this.props.label}</h2><p>Service unavailable in this view. Safety, diagnostics and other independent views remain available.</p></section>:this.props.children;}
}
