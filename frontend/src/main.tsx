import {createRoot} from 'react-dom/client';
import {OperationsApp} from './app/OperationsApp';
import './style.css';
import './operations.css';
createRoot(document.getElementById('root')!).render(<OperationsApp/>);
