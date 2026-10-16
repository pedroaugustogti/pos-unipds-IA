"""Atalho do fluxo parent.welcome_onboarding_screen.

A montagem e a sessão ficam em commons.executar_fluxo.
"""

from commons.executar_fluxo import executar

FLOW_ID = "parent.welcome_onboarding_screen"


if __name__ == "__main__":
    executar(FLOW_ID)
