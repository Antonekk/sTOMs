import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "../pages/Login"
import Register from "../pages/Register"
import NotFound from "../pages/NotFound"
import Home from "../pages/Home"
import WeeklySchedule from "../pages/WeeklySchedule";
import ActivateAccount from "../pages/ActivateAccount"
import {AuthenticatedRoute, RoleRoute, NonAuthenticatedRoute} from "../auth/Protectors"
import Layout from "../layouts/Layout";
import type React from "react";
import ScheduleOverrides from "../pages/ScheduleOverrides"
import Profile from "../pages/Profile";
import PatientNew from "../pages/PatientNew";
import PatientEdit from "../pages/PatientEdit";


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
                        path="/profil"
                        element={
                            <AuthenticatedRoute>
                                <Profile />
                            </AuthenticatedRoute>
                        }
                    />

                    <Route
                        path="/pacjenci/nowy"
                        element={
                            <RoleRoute role="CLIENT">
                                <PatientNew />
                            </RoleRoute>
                        }
                    />

                    <Route
                        path="/pacjenci/:id/edycja"
                        element={
                            <RoleRoute role="CLIENT">
                                <PatientEdit />
                            </RoleRoute>
                        }
                    />

                    <Route
                        path="/staly_grafik"
                        element={
                            <RoleRoute role="THERAPIST">
                                <WeeklySchedule />
                            </RoleRoute>
                        }
                    />

                    <Route
                        path="/wyjatki"
                        element={
                            <RoleRoute role="THERAPIST">
                                <ScheduleOverrides />
                            </RoleRoute>
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