import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';

// Mutable variable — lets each test control isAuthenticated
let mockIsAuthenticated = false;
const mockSetPendingAction = vi.fn();

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: mockIsAuthenticated,
    setPendingAction: mockSetPendingAction,
  }),
}));

import { useAuthGuard } from '../useAuthGuard';

describe('useAuthGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = false;
  });

  it('executes action immediately when user is authenticated', () => {
    mockIsAuthenticated = true;
    const openModal = vi.fn();
    const action = vi.fn();

    const { result } = renderHook(() => useAuthGuard(openModal));
    result.current.executeOrGuard(action);

    expect(action).toHaveBeenCalledOnce();
    expect(openModal).not.toHaveBeenCalled();
  });

  it('stores pending action and opens auth modal when not authenticated', () => {
    mockIsAuthenticated = false;
    const openModal = vi.fn();
    const action = vi.fn();

    const { result } = renderHook(() => useAuthGuard(openModal));
    result.current.executeOrGuard(action);

    expect(action).not.toHaveBeenCalled();
    expect(openModal).toHaveBeenCalledOnce();
    expect(mockSetPendingAction).toHaveBeenCalledOnce();
  });

  it('pending action callback wraps the original action', () => {
    mockIsAuthenticated = false;
    const openModal = vi.fn();
    const action = vi.fn();

    const { result } = renderHook(() => useAuthGuard(openModal));
    result.current.executeOrGuard(action);

    // The callback stored in setPendingAction is a factory that returns a function
    const storedFactory = mockSetPendingAction.mock.calls[0][0];
    expect(typeof storedFactory).toBe('function');
    const innerCallback = storedFactory();
    expect(typeof innerCallback).toBe('function');
  });
});
