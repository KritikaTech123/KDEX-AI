"use client";
import { useEffect } from 'react';

export default function ClientBodyFix() {
  useEffect(() => {
    try {
      const cls = 'vsc-initialized';
      if (document?.body?.classList?.contains(cls)) {
        document.body.classList.remove(cls);
      }
    } catch (e) {
      // ignore
    }
  }, []);
  return null;
}
