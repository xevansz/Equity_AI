import React from 'react'

export const Skeleton = ({ className = '', variant = 'rectangular' }) => {
  const baseClasses = 'animate-pulse bg-gray-300 dark:bg-gray-700'

  const variantClasses = {
    rectangular: 'rounded',
    circular: 'rounded-full',
    text: 'rounded h-4',
  }

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant] || variantClasses.rectangular} ${className}`}
    />
  )
}

export const CardSkeleton = () => (
  <div className="p-5 bg-surface rounded-xl shadow-sm">
    <div className="flex items-center gap-2 mb-3">
      <Skeleton className="h-6 w-20" />
      <Skeleton className="h-5 w-12" />
    </div>
    <Skeleton className="h-4 w-32 mb-4" />
    <Skeleton className="h-7 w-28 mb-2" />
    <Skeleton className="h-4 w-20 mb-4" />
    <Skeleton className="h-4 w-16" />
  </div>
)

export const DashboardSkeleton = () => (
  <div className="mt-8 space-y-6">
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-4 w-48" />
      </div>
      <Skeleton className="h-10 w-40" />
    </div>

    <div className="p-6 bg-surface rounded-lg">
      <Skeleton className="h-64 w-full mb-4" />
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-4 bg-surface rounded-lg">
        <Skeleton className="h-4 w-24 mb-2" />
        <Skeleton className="h-8 w-32" />
      </div>
      <div className="p-4 bg-surface rounded-lg">
        <Skeleton className="h-4 w-24 mb-2" />
        <Skeleton className="h-8 w-32" />
      </div>
      <div className="p-4 bg-surface rounded-lg">
        <Skeleton className="h-4 w-24 mb-2" />
        <Skeleton className="h-8 w-32" />
      </div>
    </div>

    <div className="p-6 bg-surface rounded-lg space-y-4">
      <Skeleton className="h-6 w-32 mb-4" />
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      ))}
    </div>
  </div>
)

export const ChatMessageSkeleton = () => (
  <div className="flex justify-start">
    <div className="max-w-lg px-4 py-2 rounded-lg bg-surface space-y-2">
      <Skeleton className="h-4 w-64" />
      <Skeleton className="h-4 w-48" />
      <Skeleton className="h-4 w-56" />
    </div>
  </div>
)

export default Skeleton
