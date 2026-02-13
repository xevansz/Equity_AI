import React from 'react'

const AuthLayout = ({ children }) => {
  return (
    <div className="bg-background flex items-center justify-center w-full">
      <div className="w-full max-w-md">{children}</div>
    </div>
  )
}

export default AuthLayout
