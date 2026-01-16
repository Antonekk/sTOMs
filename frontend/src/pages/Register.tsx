import React from "react";
import { Flex } from "antd";
import { SignUpForm } from "../components/storybook_components/sign_up_form/sign_up_form";
import type { SignUpFormValues } from "../components/storybook_components/sign_up_form/sign_up_form";
import Template from "../components/storybook_components/template/template"



const Register: React.FC = () => {

    const onSubmit = (values: SignUpFormValues) =>{
        console.log(values)
    }
    return (
        <Template>
            <Flex justify="center" align="center" style={{ width: '100%', height: '100%' }}>
                <SignUpForm onSubmit={onSubmit} />
            </Flex>
        </Template>
    )
}

export default Register;