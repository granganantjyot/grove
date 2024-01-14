import './TitleComponent.css';

import logo from '../grove.svg';


const TitleComponent = () => {
    return (
        <div className='title-container'>
            <p id='title'>Grove</p>
            <img id='logo' src={logo} />
        </div>
    );
}

export default TitleComponent;