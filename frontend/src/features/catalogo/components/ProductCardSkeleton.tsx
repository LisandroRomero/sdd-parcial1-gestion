export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-amber-100 overflow-hidden animate-pulse">
      {/* Image placeholder */}
      <div className="aspect-video w-full bg-gray-200" />
      {/* Content */}
      <div className="p-4 space-y-2">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        <div className="h-4 bg-gray-200 rounded w-1/2" />
        <div className="h-5 bg-amber-100 rounded w-1/3 mt-2" />
      </div>
    </div>
  )
}
