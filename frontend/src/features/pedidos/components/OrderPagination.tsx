interface OrderPaginationProps {
  page: number
  pages: number
  total: number
  onPageChange: (page: number) => void
}

export function OrderPagination({ page, pages, total, onPageChange }: OrderPaginationProps) {
  if (pages <= 1) return null

  return (
    <div className="flex items-center justify-between pt-4">
      <p className="text-sm text-gray-500">
        Página {page} de {pages} ({total} pedidos)
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          Anterior
        </button>

        {/* Page number buttons */}
        {Array.from({ length: Math.min(pages, 5) }, (_, i) => {
          const pageNum = Math.max(1, Math.min(page - 2, pages - 4)) + i
          if (pageNum > pages) return null
          return (
            <button
              key={pageNum}
              type="button"
              onClick={() => onPageChange(pageNum)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                pageNum === page
                  ? 'bg-primary text-white border-primary'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {pageNum}
            </button>
          )
        })}

        <button
          type="button"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          Siguiente
        </button>
      </div>
    </div>
  )
}
