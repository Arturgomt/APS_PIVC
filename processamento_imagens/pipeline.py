"""Aquisição já recebida -> qualidade e pontos faciais -> rosto alinhado SFace."""

from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from .alinhamento import Preparador, PreparadorSFace
from .configuracao import Configuracao, FORMATO_SFACE
from .tipos import Qualidade, Resultado, Rosto, Status


class ProcessadorFacial:
    def __init__(self, config: Configuracao | None = None, *,
                 preparador: Preparador | None = None, pasta_modelos: str | Path | None = None):
        self.config = config if config is not None else Configuracao()
        self.preparador = preparador if preparador is not None else PreparadorSFace(self.config, pasta_modelos)
        self.clahe = cv2.createCLAHE(clipLimit=self.config.clip_limit, tileGridSize=(8, 8))

    def processar(self, imagem: np.ndarray | None, *, incluir_etapas: bool = False) -> Resultado:
        inicio = perf_counter()
        if not self._imagem_valida(imagem):
            return Resultado(
                Status.IMAGEM_INVALIDA, "Informe uma imagem colorida uint8 BGR ou BGRA não vazia.",
                tempo_ms=(perf_counter() - inicio) * 1000,
            )
        altura, largura = imagem.shape[:2]
        bgr = cv2.cvtColor(imagem, cv2.COLOR_BGRA2BGR) if imagem.shape[2] == 4 else imagem.copy()
        if largura > self.config.largura_maxima:
            nova_altura = max(1, round(altura * self.config.largura_maxima / largura))
            bgr = cv2.resize(bgr, (self.config.largura_maxima, nova_altura), interpolation=cv2.INTER_AREA)
        h, w = bgr.shape[:2]
        cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        resultado = Resultado(
            Status.SEM_ROSTO, "Nenhum rosto detectado.",
            original_hw=(altura, largura), processada_hw=(h, w),
        )
        if incluir_etapas:
            suavizada = cv2.GaussianBlur(cinza, (3, 3), 0)
            resultado.etapas = {
                "01_redimensionada_bgr": bgr.copy(),
                "02_cinza_qualidade": cinza,
                "03_suavizada_didatica": suavizada,
                "04_clahe_didatica": self.clahe.apply(suavizada),
            }
        # Detecção e alinhamento usam BGR preservado, nunca a imagem cinza/CLAHE.
        deteccoes = self.preparador.detectar(bgr) if min(h, w) >= self.config.tamanho_minimo_rosto else None
        linhas = [] if deteccoes is None else list(deteccoes)
        linhas_validas = []
        falha_alinhamento = False
        for deteccao in linhas:
            linha = np.asarray(deteccao, dtype=np.float32)
            if not self._deteccao_valida(linha, w, h):
                falha_alinhamento = True
                continue
            linhas_validas.append(linha)
        linhas_validas.sort(key=lambda d: (float(d[0]), float(d[1])))
        for linha in linhas_validas:
            x, y, cw, ch = (float(v) for v in linha[:4])
            x1, y1 = max(0, int(np.floor(x))), max(0, int(np.floor(y)))
            x2, y2 = min(w, int(np.ceil(x + cw))), min(h, int(np.ceil(y + ch)))
            if x2 <= x1 or y2 <= y1:
                falha_alinhamento = True
                continue
            qualidade = self._qualidade(cinza[y1:y2, x1:x2])
            pontos = linha[4:14].reshape(5, 2)
            pontos_originais = pontos * np.array([largura / w, altura / h], dtype=np.float32)
            ox1, oy1 = int(x1 * largura / w), int(y1 * altura / h)
            ox2, oy2 = min(largura, int(np.ceil(x2 * largura / w))), min(altura, int(np.ceil(y2 * altura / h)))
            rosto = Rosto(
                caixa_original=(ox1, oy1, ox2 - ox1, oy2 - oy1),
                caixa_processada=(x1, y1, x2 - x1, y2 - y1),
                pontos_original=pontos_originais.tolist(),
                confianca_deteccao=float(linha[14]), qualidade=qualidade,
            )
            try:
                alinhada = self.preparador.alinhar(bgr, linha)
                if not isinstance(alinhada, np.ndarray) or alinhada.shape != FORMATO_SFACE or alinhada.dtype != np.uint8:
                    falha_alinhamento = True
                else:
                    rosto.imagem_alinhada_bgr = np.ascontiguousarray(alinhada)
            except cv2.error:
                falha_alinhamento = True
            resultado.rostos.append(rosto)

        if falha_alinhamento:
            resultado.status = Status.ALINHAMENTO_INVALIDO
            resultado.mensagem = "Não foi possível alinhar todos os rostos. Ajuste a posição e repita a captura."
        elif len(resultado.rostos) > 1:
            resultado.status = Status.MULTIPLOS_ROSTOS
            resultado.mensagem = "Mais de um rosto detectado. Mantenha apenas uma pessoa no enquadramento."
        elif resultado.rostos:
            if resultado.rostos[0].qualidade.aprovada:
                resultado.status = Status.OK
                resultado.mensagem = "Rosto alinhado e preparado para o reconhecimento."
            else:
                resultado.status = Status.QUALIDADE_INSUFICIENTE
                resultado.mensagem = "Ajuste a captura: " + "; ".join(resultado.rostos[0].qualidade.problemas) + "."
        if incluir_etapas:
            anotada = bgr.copy()
            for rosto in resultado.rostos:
                x, y, cw, ch = rosto.caixa_processada
                cv2.rectangle(anotada, (x, y), (x + cw, y + ch), (0, 180, 0), 2)
                pontos_processados = np.asarray(rosto.pontos_original) * np.array([w / largura, h / altura])
                for px, py in pontos_processados:
                    cv2.circle(anotada, (round(float(px)), round(float(py))), 2, (0, 180, 255), -1)
            resultado.etapas["05_deteccao_pontos"] = anotada
        resultado.tempo_ms = (perf_counter() - inicio) * 1000
        return resultado

    @staticmethod
    def _imagem_valida(imagem) -> bool:
        return (isinstance(imagem, np.ndarray) and imagem.dtype == np.uint8 and imagem.size > 0
                and imagem.ndim == 3 and imagem.shape[2] in (3, 4))

    @staticmethod
    def _deteccao_valida(linha, largura, altura) -> bool:
        if linha.shape != (15,) or not np.isfinite(linha).all() or np.any(linha[2:4] <= 0):
            return False
        if not 0 <= float(linha[14]) <= 1:
            return False
        pontos = linha[4:14].reshape(5, 2)
        if np.any(pontos < 0) or np.any(pontos[:, 0] >= largura) or np.any(pontos[:, 1] >= altura):
            return False
        return bool(np.linalg.norm(pontos[0] - pontos[1]) > 1 and np.linalg.matrix_rank(pontos - pontos.mean(axis=0)) == 2)

    def _qualidade(self, cinza: np.ndarray) -> Qualidade:
        brilho = float(cinza.mean())
        nitidez = float(cv2.Laplacian(cinza, cv2.CV_64F).var())
        problemas = []
        if min(cinza.shape) < self.config.tamanho_minimo_rosto:
            problemas.append("rosto pequeno; aproxime-se da câmera")
        if brilho < self.config.brilho_minimo:
            problemas.append("iluminação baixa")
        if brilho > self.config.brilho_maximo:
            problemas.append("iluminação excessiva")
        if nitidez < self.config.nitidez_minima:
            problemas.append("nitidez baixa")
        return Qualidade(brilho, nitidez, problemas)
