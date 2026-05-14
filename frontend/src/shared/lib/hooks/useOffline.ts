import { useEffect, useState } from 'react'

function getNavigatorOnline() {
  return typeof navigator === 'undefined' ? true : navigator.onLine
}

export function useOffline() {
  const [isOffline, setIsOffline] = useState(() => !getNavigatorOnline())

  useEffect(() => {
    function handleOnline() {
      setIsOffline(false)
    }

    function handleOffline() {
      setIsOffline(true)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    setIsOffline(!getNavigatorOnline())

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return isOffline
}
