import {useParams, useNavigate} from "react-router-dom"
import { useEffect, useState} from "react"
import {activate} from "../api/auth"
import Loading from "../components/storybook_components/auth_loading/auth_loading"
import AccountActivation from "../components/storybook_components/account_activation/account_activation"



export const ActivateAccount: React.FC = () => {
    const {uid, token} = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState<boolean>(true);
    const [success, setSuccess] = useState<boolean>(false);

    useEffect(() => {
        const activateAccount = async () => {
            try{
                await activate({uid, token});
                setSuccess(true)
            }
            catch{
                setSuccess(false);
            }
            finally{
                setLoading(false);
            }
        }
        if(uid && token){
            void activateAccount();
        }
    }, [uid, token]);


    if(loading){
        return <Loading></Loading>
    }

    return(
        <AccountActivation
            success={success}
            title={success ? "Twoje konto zostało aktywowane!" : "Proces aktywacji nie przebiegł pomyślnie."}
            subTitle={success ? "Możesz się teraz zalogować za pomocą adresu email i hasła" : "Twój link aktywacyjny jest niepoprawny lub wygasł. Spróbuj ponownie."}
            onClick={success ? () => {void navigate("/login")} : () => {void navigate("/rejestracja")}}
        />

    )


}

export default ActivateAccount;