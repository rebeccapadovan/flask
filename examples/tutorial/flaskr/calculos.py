from flask import Blueprint, render_template, request

bp = Blueprint("calculos", __name__, url_prefix="/painel")


@bp.route("/", methods=("GET", "POST"))
def index():
    irpf = None
    decimo_terceiro = None
    tipo_calculo = None
    erro = None

    if request.method == "POST":
        tipo_calculo = request.form.get("tipo_calculo")

        try:
            salario = float(request.form.get("salario", 0))

            if salario < 0:
                raise ValueError

            if tipo_calculo == "irpf":
                # Estimativa simplificada do IRPF mensal
                if salario <= 2428.80:
                    irpf = 0
                elif salario <= 2826.65:
                    irpf = salario * 0.075 - 182.16
                elif salario <= 3751.05:
                    irpf = salario * 0.15 - 394.16
                elif salario <= 4664.68:
                    irpf = salario * 0.225 - 675.49
                else:
                    irpf = salario * 0.275 - 908.73

                irpf = max(0, irpf)

            elif tipo_calculo == "decimo_terceiro":
                meses = int(request.form.get("meses", 0))

                if not 1 <= meses <= 12:
                    erro = "Informe uma quantidade de meses entre 1 e 12."
                else:
                    decimo_terceiro = salario / 12 * meses

            else:
                erro = "Selecione uma calculadora válida."

        except (ValueError, TypeError):
            erro = "Informe valores numéricos válidos e não negativos."
            irpf = None
            decimo_terceiro = None

    return render_template(
        "calculos/index.html",
        irpf=irpf,
        decimo_terceiro=decimo_terceiro,
        tipo_calculo=tipo_calculo,
        erro=erro,
    )
