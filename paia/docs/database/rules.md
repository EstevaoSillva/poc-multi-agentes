**Descrição:** Define o banco de dados que será usado, bem como regras e boas práticas para criação da estrutura do banco de dados.


- *Tipo do banco de dados:* PostgreSQL 17
- *Padrão para criação de DDL*

    1. Nome de tabelas devem ser sempre em minúsculo, em inglês, no singular e separados por _
    2. Nome de colunas devem ser em minúsculo, em inglês e separados por _
    3. As PKs de tabelas devem sempre se chamar id e ser do tipo BIGSERIAL
    4. As FKs devem sempre ter id_${tabela_de_origem}
    5. Campos do tipo texto devem sempre ter o tx na frente do nome do campo, exemplo: tx_name
    5. Campos do tipo númerico, inteiros ou pontos flutuantes devem sempre ter o nb na frente do nome do campo, exemplo: nb_salary
    6. Campos que definem valores concretos como por exemplo sexo, devem sempre ter na frente cs, exemplo: cs_gender
    7. Campos do tipo data ou datetime devem sempre ter o dt na frente, exemplo: dt_birth
    
