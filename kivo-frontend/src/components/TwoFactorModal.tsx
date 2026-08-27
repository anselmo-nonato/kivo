"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { ShieldCheck, X, Copy, Check, AlertTriangle, KeyRound } from "lucide-react";

interface TwoFactorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TwoFactorModal: React.FC<TwoFactorModalProps> = ({ isOpen, onClose }) => {
  const { user, reloadUserData } = useAuth();
  const [step, setStep] = useState<"initial" | "setup" | "disable">("initial");
  const [qrCode, setQrCode] = useState<string>("");
  const [secret, setSecret] = useState<string>("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [code, setCode] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [copied, setCopied] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleStartSetup = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/auth/2fa/setup");
      setQrCode(res.data.qr_code_base64);
      setSecret(res.data.secret);
      setBackupCodes(res.data.backup_codes);
      setStep("setup");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao gerar configuração de 2FA.");
    } finally {
      setLoading(false);
    }
  };

  const handleEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/2fa/enable", { code: code.trim() });
      await reloadUserData();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Código inválido. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/2fa/disable", { password, code: code.trim() });
      await reloadUserData();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao desativar 2FA. Verifique a senha e o código.");
    } finally {
      setLoading(false);
    }
  };

  const copyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">Autenticação em 2 Etapas (2FA)</h2>
            <p className="text-xs text-slate-500">Padrão RFC 6238 TOTP (Google Authenticator / Authy)</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Estado 1: 2FA Já Ativo */}
        {user?.mfa_enabled && step === "initial" && (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm">
              <p className="font-bold flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600" /> Sua conta está protegida por 2FA!
              </p>
              <p className="text-xs text-emerald-700 mt-1">
                A cada login, será solicitado o código gerado pelo aplicativo autenticador no seu celular.
              </p>
            </div>

            <button
              onClick={() => setStep("disable")}
              className="w-full py-2.5 rounded-xl border border-red-200 text-red-600 font-bold hover:bg-red-50 text-sm transition-colors"
            >
              Desativar 2FA
            </button>
          </div>
        )}

        {/* Estado 2: Iniciar Configuração de 2FA */}
        {!user?.mfa_enabled && step === "initial" && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              A autenticação em 2 etapas adiciona uma camada extra de segurança à sua conta KIVO. Além da sua senha, você usará um código temporário de 6 dígitos gerado pelo Google Authenticator.
            </p>

            <button
              onClick={handleStartSetup}
              disabled={loading}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors"
            >
              {loading ? "Gerando chaves..." : "Configurar Google Authenticator"}
            </button>
          </div>
        )}

        {/* Estado 3: Passo a Passo do Setup (QR Code + Backup Codes) */}
        {step === "setup" && (
          <form onSubmit={handleEnable} className="space-y-5">
            <div className="text-center space-y-2">
              <p className="text-xs font-semibold text-slate-500">1. Escaneie o QR Code no seu aplicativo:</p>
              {qrCode && (
                <div className="inline-block p-3 rounded-2xl bg-white border border-slate-200 shadow-xs">
                  <img src={qrCode} alt="QR Code 2FA" className="w-44 h-44 mx-auto" />
                </div>
              )}
              <p className="text-[11px] text-slate-400 font-mono">Chave Manual: {secret}</p>
            </div>

            {/* Códigos de Backup */}
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                <span>2. Guarde seus 8 Códigos de Backup:</span>
                <button
                  type="button"
                  onClick={copyBackupCodes}
                  className="flex items-center gap-1 text-emerald-600 hover:text-emerald-700 font-semibold"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copiado!" : "Copiar"}</span>
                </button>
              </div>
              <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px] text-slate-600">
                {backupCodes.map((bc, idx) => (
                  <span key={idx} className="bg-white px-2 py-1 rounded border border-slate-200 text-center">
                    {bc}
                  </span>
                ))}
              </div>
            </div>

            {/* Validação do Código */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">
                3. Digite o código de 6 dígitos gerado no app para confirmar:
              </label>
              <input
                type="text"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                placeholder="000000"
                required
                className="w-full text-center text-2xl font-mono tracking-widest py-2 rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500 font-bold"
              />
            </div>

            <button
              type="submit"
              disabled={loading || code.length !== 6}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-sm shadow-md shadow-emerald-500/20 transition-colors"
            >
              {loading ? "Verificando..." : "Confirmar e Ativar 2FA"}
            </button>
          </form>
        )}

        {/* Estado 4: Desativar 2FA */}
        {step === "disable" && (
          <form onSubmit={handleDisable} className="space-y-4">
            <p className="text-xs text-slate-500">
              Para desativar a autenticação em 2 etapas, confirme sua senha e o código atual do seu aplicativo.
            </p>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Sua Senha:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Código de 6 Dígitos:</label>
              <input
                type="text"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                placeholder="000000"
                required
                className="w-full text-center text-xl font-mono py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 font-bold"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setStep("initial")}
                className="w-1/2 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-sm"
              >
                Voltar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="w-1/2 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-sm"
              >
                {loading ? "Desativando..." : "Desativar"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
