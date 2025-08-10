import {Link} from "react-router-dom";

const NotFoundPage = () => {
    return (
        <div className="flex flex-col w-screen min-h-screen justify-center items-center">
            <h1>404: Page not Found!</h1>
            <Link to={"/"}>
                <button>Return to Home</button>
            </Link>
        </div>
    );
};

export default NotFoundPage;