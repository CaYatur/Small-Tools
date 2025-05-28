import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <nav>
            <ul>
                <li>
                    <Link to="/">Home</Link>
                </li>
                <li>
                    <Link to="/editor">Code Editor</Link>
                </li>
                <li>
                    <Link to="/console">Console</Link>
                </li>
                <li>
                    <Link to="/packages">Packages</Link>
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;