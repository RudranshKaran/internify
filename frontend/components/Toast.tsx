'use client'

import { ToastContainer, toast as toastify } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

export function Toast() {
  return (
    <ToastContainer
      position="top-right"
      autoClose={5000}
      hideProgressBar={false}
      newestOnTop
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="light"
    />
  )
}

export const toast = {
  success: (message: string) => toastify.success(message),
  error: (message: string) => toastify.error(message),
  info: (message: string) => toastify.info(message),
  warning: (message: string) => toastify.warning(message),
}
