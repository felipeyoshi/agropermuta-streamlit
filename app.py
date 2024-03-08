import streamlit as st
import requests
import pandas as pd

st.image('logo.jpg')

email = st.text_input('Email')
valor_bem = st.number_input('Valor', min_value=0.0, format='%f')

if st.button('Simular'):
    # Call the API with all parameters
    data = {
        "data_inicial": "2024-02-26",
        "valor_bem": valor_bem,
        "entrada": 0,
        "vencimento_primeira_parcela": "2024-10-30",
        "vencimento_segunda_parcela": "2025-03-31",
        "taxa_seguro": 0.03,
        "custo_rastreador": 7000.00,
        "capitalizacao_ano": 0.1050,
        "numero_parcelas": 6,
        "taxa_desagio": 0.0155,
        "data_desconto": "2024-02-29"
    }
    
    response = requests.post('http://agropermuta.onrender.com/simulador', json=data)

    def format_currency(value):
        return 'R$ ' + f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def format_number(value):
        return f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.round(2)

        if '@agropermuta.com.br' not in email:
            df = df[['pmt', 'Periodicidade', 'Parcela']]
            df.rename(columns={'pmt': 'Parcela', 'Periodicidade': 'Vencimento', 'Parcela': 'Valor da Parcela'}, inplace=True)
            df['Vencimento'] = pd.to_datetime(df['Vencimento']).dt.strftime('%d/%m/%Y')
            df['Valor da Parcela'] = df['Valor da Parcela'].apply(format_currency)
        
        else:
            df['Periodicidade'] = pd.to_datetime(df['Periodicidade']).dt.strftime('%d/%m/%Y')
            df['Principal'] = df['Principal'].apply(format_number)
            df['Seguro'] = df['Seguro'].apply(format_number)
            df['Amortização'] = df['Amortização'].apply(format_number)
            df['Juros'] = df['Juros'].apply(format_number)
            df['Parcela'] = df['Parcela'].apply(format_number)
            df['Valor Presente'] = df['Valor Presente'].apply(format_number)

        # Aplicando estilos CSS com o Styler
        styler = df.style.hide(axis="index").set_table_attributes('style="width:100%;"').set_properties(**{'text-align': 'center',}).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])

        # Renderiza o DataFrame como HTML
        html = styler.to_html(index=False)

        # Usa o markdown do Streamlit para exibir o HTML com o estilo
        st.markdown(html, unsafe_allow_html=True)

        st.markdown(
            """
            <small><br>Taxas de juros podem ser alteradas sem aviso prévio.<br></small>
            <small>Liberação dos recursos somente após:<br></small>
            <small>- Pagamento da Estruturação<br></small>
            <small>- Pagamento da Entrada, caso haja</small>
            """,
            unsafe_allow_html=True
        )

    else:
        st.error(f'Error: {response.status_code}')