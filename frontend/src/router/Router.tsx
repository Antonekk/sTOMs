import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "../pages/Login"
import Register from "../pages/Register"
import NotFound from "../pages/NotFound"
import Home from "../pages/Home"
import ActivateAccount from "../pages/ActivateAccount"
import {AuthenticatedRoute, RoleRoute, NonAuthenticatedRoute} from "../auth/Protectors"
import Layout from "../layouts/Layout";
import type React from "react";


// Clear local storage before registering to avoid sending pre-existing tokens
const PreRegister: React.FC = () => {
  localStorage.clear()
  return <Register />
}

const Router: React.FC = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route element={<Layout />}>
                    <Route 
                        path="/"
                        element={
                            <Home />
                        }
                    />
                    <Route 
                        path="/login" 
                        element={
                            <NonAuthenticatedRoute>
                                <Login/>
                            </NonAuthenticatedRoute>
                        }
                    />
                    <Route 
                        path="/rejestracja" 
                        element={
                            <NonAuthenticatedRoute>
                                <PreRegister/>
                            </NonAuthenticatedRoute>
                        }
                    />
                    <Route 
                        path="/aktywacja/:uid/:token" 
                        element={
                            <NonAuthenticatedRoute>
                                <ActivateAccount/>
                            </NonAuthenticatedRoute>
                        }
                    />
                    <Route 
                        path='/panel'
                        element={
                            <AuthenticatedRoute>
                                <Home />
                            </AuthenticatedRoute>
                        }
                    />

                    <Route 
                        path="*" 
                        element={<NotFound />} 
                    />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default Router;