import { create } from 'zustand'

export type PaymentStatus =
  | 'idle'
  | 'processing'
  | 'approved'
  | 'rejected'
  | 'pending'

export interface PaymentState {
  preferenceId: string | null
  status: PaymentStatus
  paymentId: number | null
  error: string | null
  setPreferenceId: (id: string) => void
  setApproved: (paymentId: number) => void
  setRejected: (error?: string) => void
  setProcessing: () => void
  resetState: () => void
}

const initialState = {
  preferenceId: null as string | null,
  status: 'idle' as PaymentStatus,
  paymentId: null as number | null,
  error: null as string | null,
}

export const usePaymentStore = create<PaymentState>((set) => ({
  ...initialState,

  setPreferenceId: (id) =>
    set({ preferenceId: id, status: 'pending' }),

  setApproved: (paymentId) =>
    set({ status: 'approved', paymentId }),

  setRejected: (error) =>
    set({ status: 'rejected', error: error ?? null }),

  setProcessing: () =>
    set({ status: 'processing' }),

  resetState: () =>
    set({ ...initialState }),
}))

export const paymentStore = usePaymentStore
