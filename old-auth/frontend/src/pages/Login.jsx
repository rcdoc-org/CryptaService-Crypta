import Form from '../components/Form';

function Login() {
    return <Form route='/api/v1/token/' method='login' />;
}

export default Login;