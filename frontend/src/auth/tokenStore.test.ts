// Concept by MrHan (08974747477)
import { describe, expect, it, vi } from 'vitest';
import { clearAccessToken, getAccessToken, setAccessToken, subscribe } from './tokenStore';

describe('tokenStore', () => {
  it('starts null', () => {
    expect(getAccessToken()).toBeNull();
  });

  it('sets and gets the token', () => {
    setAccessToken('abc');
    expect(getAccessToken()).toBe('abc');
  });

  it('clears the token', () => {
    setAccessToken('abc');
    clearAccessToken();
    expect(getAccessToken()).toBeNull();
  });

  it('notifies subscribers on change', () => {
    const listener = vi.fn();
    const unsub = subscribe(listener);
    setAccessToken('x');
    clearAccessToken();
    expect(listener).toHaveBeenCalledTimes(2);
    unsub();
    setAccessToken('y');
    expect(listener).toHaveBeenCalledTimes(2); // no longer called after unsubscribe
  });

  it('never touches web storage', () => {
    const setItem = vi.spyOn(Storage.prototype, 'setItem');
    setAccessToken('secret-token');
    clearAccessToken();
    expect(setItem).not.toHaveBeenCalled();
  });
});
