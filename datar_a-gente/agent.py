from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='diario_intuitivo',
    #Descripción humana
    description='Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción',
    #Instrucción para el agente
    instruction='Crea un input de entrada para ingresar un emoji o signo de la iteración',
)
