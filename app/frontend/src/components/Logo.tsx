// Logo AEDane: sygnet (serce z błyskawicą) + logotyp „AEDane”, Noto Sans Semi-Bold, #008C15.
// Geometria 1:1 z visual/Logo.svg (Kuba, branch kvba); księga znaku: visual/podstawowa_ksiega_znaku.pdf.
// Pole ochronne = 1/3 wysokości sygnetu (CSS .logo), rozmiar minimalny w internecie: 56 px szerokości.
const SERCE =
  "m -346.65721,8.6019926 a 29.289454,28.833691 0 0 0 -7.5808,0.98293 29.289454,28.833691 0 0 0 -20.711,20.3886964 29.289454,28.833691 0 0 0 7.5809,27.85041 l 41.4213,40.777959 41.4214,-40.777959 a 29.289454,28.833691 0 0 0 7.58079,-27.85041 29.289454,28.833691 0 0 0 -20.71041,-20.3886964 29.289454,28.833691 0 0 0 -28.29178,7.4622564 29.289454,28.833691 0 0 0 -20.7104,-8.4451864 z m 19.57239,13.3213764 a 1.3018787,1.2816207 0 0 1 1.33748,1.13478 l 2.80551,24.08174 a 2.9316121,2.8859943 0 0 0 2.91229,2.55713 h 11.09657 a 1.607783,1.5827649 0 0 1 1.43467,2.29681 l -16.74091,32.59144 a 1.3197078,1.2991722 0 0 1 -2.48963,-0.4489 l -2.5744,-23.83587 a 2.9073636,2.8621231 0 0 0 -2.89081,-2.55936 h -10.73776 a 1.6360254,1.6105678 0 0 1 -1.4714,-2.31462 l 16.19166,-32.78279 a 1.3018787,1.2816207 0 0 1 1.12673,-0.72036 z";

/** Sam sygnet (forma alternatywna z księgi). */
export function Serce({ rozmiar = 40 }: { rozmiar?: number }) {
  return (
    <svg width={rozmiar} height={rozmiar * 0.9} viewBox="-377 7 103 93" aria-hidden="true" focusable="false">
      <path fill="#008c15" fillRule="evenodd" d={SERCE} />
    </svg>
  );
}

export function Logo() {
  return (
    <a href="/" className="logo" aria-label="AEDane: strona główna">
      <svg className="logo-znak" viewBox="0 0 1439.0273 360.00003" aria-hidden="true" focusable="false">
        <g transform="translate(-4911.9579,656.73454)">
          <g transform="matrix(4.0000008,0,0,4.0000008,6415.7454,-691.14252)" fill="#008c15">
            <path fillRule="evenodd" d={SERCE} />
            <text x="-253.85716" y="76.180695" fontFamily="'Noto Sans', sans-serif" fontWeight={600} fontSize="63.8718">
              AEDane
            </text>
          </g>
        </g>
      </svg>
    </a>
  );
}
