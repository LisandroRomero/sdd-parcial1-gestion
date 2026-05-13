interface CatalogPaginationProps {
  page: number
  pages: number
  onPageChange: (page: number) => void
}

export function CatalogPagination({ page, pages, onPageChange }: CatalogPaginationProps) {
  if (pages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-4 mt-8">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="px-4 py-2 text-sm font-medium rounded-lg border border-amber-200 text-amber-700 hover:bg-amber-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        ← Anterior
      </button>

      <span className="text-sm text-gray-600">
        Página <span className="font-semibold text-gray-900">{page}</span> de{' '}
        <span className="font-semibold text-gray-900">{pages}</span>
      </span>

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= pages}
        className="px-4 py-2 text-sm font-medium rounded-lg border border-amber-200 text-amber-700 hover:bg-amber-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Siguiente →
      </button>
    </div>
  )
}
