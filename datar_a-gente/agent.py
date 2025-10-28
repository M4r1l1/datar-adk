from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='diario_intuitivo',
    #Descripción humana
    description='Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción con el territorio',
    #Instrucción para el agente
    instruction='Crea un input de entrada para ingresar un emoji por cada minuto y analizar que emoción interpretas cada vez que agregar un nuevo emoji y tu interpretación global, cada vez que se agregan más. Una transición individual y panorama general de interpretación',
)
