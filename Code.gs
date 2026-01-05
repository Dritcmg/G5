/**
 * G5 FUTEBOL - SISTEMA DE GESTÃO DE TREINOS
 * Automatização para geração de planilhas de treinos mensais.
 */

// --- CONFIGURAÇÕES ---

const CONFIG = {
  CATEGORIAS: {
    'Sub 17': [2009, 2010],
    'Sub 15': [2011],
    'Sub 14': [2012],
    'Sub 13': [2013],
    'Sub 12': [2014],
    'Sub 11': [2015],
    'Sub 10': [2016],
    'Sub 9':  [2017]
  },
  TREINOS: [
    'Físico', 'Técnico', 'Tático', 'Físico', 'Técnico', 
    'Técnico', 'Tático', 'Vídeo', 'Amistoso', 'Paulista', 
    'Teste Fisico', 'Coletivo', 'Palestra', 'Academia'
  ],
  LEGENDA_ATLETAS: ['1', '2', '3', 'F', 'DM'], // 1=Abaixo, 2=Media, 3=Destacou, F=Faltou, DM=Lesao
  LEGENDA_TREINOS: ['1', '2', '3', 'FO', 'AM', 'CH'] // 1=Ruim, 2=Media, 3=Bom, FO=Folga, AM=Amistoso, CH=Choveu
};

const SHEETS = {
  DB_ATLETAS: 'DB_ATLETAS',
  CONFIG_INTERFACE: 'INTERFACE_TREINOS' // Pode ser criado se não existir
};

// --- MENUS ---

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('⚽ G5 Sistema')
    .addItem('📅 Gerar Planilha de Treinos', 'mostrarDialogoGeracao')
    .addToUi();
}

// --- INTERFACE DE GERAÇÃO ---

function mostrarDialogoGeracao() {
  const ui = SpreadsheetApp.getUi();
  
  // Usaremos um prompt simples para facilitar, ou uma interface HTML se preferir mais complexidade.
  // Vamos tentar ler da aba CONFIG ou pedir via Prompt.
  // Para robustez, vamos pedir via Browser.inputBox
  
  const responseMes = ui.prompt('Gerar Treinos', 'Digite o número do Mês (1-12):', ui.ButtonSet.OK_CANCEL);
  if (responseMes.getSelectedButton() !== ui.Button.OK) return;
  
  const mes = parseInt(responseMes.getResponseText());
  if (isNaN(mes) || mes < 1 || mes > 12) {
    ui.alert('Mês inválido! Digite um número entre 1 e 12.');
    return;
  }
  
  const responseCat = ui.prompt('Gerar Treinos', 'Digite a Categoria (Ex: Sub 14):', ui.ButtonSet.OK_CANCEL);
  if (responseCat.getSelectedButton() !== ui.Button.OK) return;
  
  const categoria = responseCat.getResponseText().trim();
  if (!CONFIG.CATEGORIAS[categoria]) {
    let validas = Object.keys(CONFIG.CATEGORIAS).join(', ');
    ui.alert(`Categoria não encontrada!\nCategorias válidas: ${validas}`);
    return;
  }
  
  gerarPlanilhaTreinos(mes, categoria);
}

// --- CORE: GERAR PLANILHA ---

function gerarPlanilhaTreinos(mes, categoria) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const year = new Date().getFullYear(); // Assume ano atual
  const sheetName = `Treinos_${categoria}_${mes}_${year}`;
  
  // Verificar se já existe e deletar (opcional, ou alertar)
  let sheet = ss.getSheetByName(sheetName);
  if (sheet) {
    const ui = SpreadsheetApp.getUi();
    const resp = ui.alert('Aba já existe', `A aba '${sheetName}' já existe. Deseja sobrescrevê-la?`, ui.ButtonSet.YES_NO);
    if (resp !== ui.Button.YES) return;
    ss.deleteSheet(sheet);
  }
  
  sheet = ss.insertSheet(sheetName);
  
  // 1. Configurar Estrutura de Datas
  const daysInMonth = new Date(year, mes, 0).getDate();
  const weekDays = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];
  
  // Cabeçalhos Fixos
  sheet.getRange('A1').setValue('CATEGORIA:').setFontWeight('bold');
  sheet.getRange('B1').setValue(categoria).setFontColor('#134F5C').setFontWeight('bold');
  
  sheet.getRange('A2').setValue('MÊS:').setFontWeight('bold');
  sheet.getRange('B2').setValue(`${mes}/${year}`).setFontColor('#134F5C').setFontWeight('bold');
  
  // Gerar Colunas de Dias
  let startCol = 3; // Começa na Coluna C
  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, mes - 1, d);
    const wd = weekDays[date.getDay()];
    
    // Linha 3: Dia da Semana (D, S, T...)
    sheet.getCell(3, startCol + d - 1).setValue(wd).setHorizontalAlignment('center').setFontWeight('bold');
    // Linha 4: Dia do Mês (1, 2, 3...)
    sheet.getCell(4, startCol + d - 1).setValue(d).setHorizontalAlignment('center');
    
    // Pintar Fim de Semana
    if (wd === 'D' || wd === 'S') {
      sheet.getRange(3, startCol + d - 1, 100, 1).setBackground('#F4F6F7'); // Cinza leve
    }
  }
  
  // Ajustar largura das colunas de dias
  sheet.setColumnWidths(startCol, daysInMonth, 30);
  
  // 2. Seção de Tipos de Treino (Linhas)
  let currentRow = 6;
  CONFIG.TREINOS.forEach(tipo => {
    sheet.getRange(currentRow, 1).setValue(tipo).setFontWeight('bold');
    
    // Checkboxes ou 'x' para marcar
    const rangeCheck = sheet.getRange(currentRow, startCol, 1, daysInMonth);
    
    // Opção A: Checkbox (Mais moderno)
    // rangeCheck.insertCheckboxes();
    
    // Opção B: Validação 'x' (Conforme pedido "checklist de x")
    const rule = SpreadsheetApp.newDataValidation().requireValueInList(['x'], true).build();
    rangeCheck.setDataValidation(rule);
    
    currentRow++;
  });
  
  // Linha de Resumo do Treino (Nota)
  currentRow++;
  sheet.getRange(currentRow, 1).setValue('AVALIAÇÃO TREINO').setFontWeight('bold').setBackground('#0C343D').setFontColor('white');
  const rangeAval = sheet.getRange(currentRow, startCol, 1, daysInMonth);
  const ruleAval = SpreadsheetApp.newDataValidation().requireValueInList(CONFIG.LEGENDA_TREINOS, true).build();
  rangeAval.setDataValidation(ruleAval);
  rangeAval.setBackground('#D6EAF8'); // Azul claro destaque
  
  // 3. Seção de Atletas
  currentRow += 2; // Espaço
  sheet.getRange(currentRow, 1).setValue('ATLETAS').setFontWeight('bold').setFontSize(12);
  currentRow++;
  
  const atletas = getAthletesByYear(CONFIG.CATEGORIAS[categoria]);
  
  if (atletas.length === 0) {
    sheet.getRange(currentRow, 1).setValue('Nenhum atleta encontrado para esta categoria.');
  } else {
    atletas.forEach(atleta => {
      sheet.getRange(currentRow, 1).setValue(atleta.nome); // Coluna A: Nome
      
      // Validação de Notas/Presença (1-3, F, DM)
      const rangeAtleta = sheet.getRange(currentRow, startCol, 1, daysInMonth);
      const ruleAtleta = SpreadsheetApp.newDataValidation().requireValueInList(CONFIG.LEGENDA_ATLETAS, true).build();
      rangeAtleta.setDataValidation(ruleAtleta);
      
      currentRow++;
    });
  }
  
  // 4. Formatação Final
  sheet.setColumnWidth(1, 200); // Coluna A mais larga para nomes
  sheet.getRange(1, 1, currentRow, startCol + daysInMonth).setBorder(true, true, true, true, true, true); // Bordas simples
  
  // Congelar painéis
  sheet.setFrozenColumns(2);
  sheet.setFrozenRows(5);
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Planilha gerada com sucesso!', 'Concluído');
}

// --- HELPER: BUSCAR ATLETAS ---

function getAthletesByYear(targetYears) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheetDB = ss.getSheetByName(SHEETS.DB_ATLETAS);
  
  if (!sheetDB) {
    throw new Error(`Aba '${SHEETS.DB_ATLETAS}' não encontrada!`);
  }
  
  const data = sheetDB.getDataRange().getValues();
  const headers = data[0]; // Assumindo linha 1 cabeçalhos, ajustar se necessário
  
  // Mapear indices das colunas (Assumindo estrutura do script Python anterior)
  // ID, Nome, Data Nasc, Categoria, Posição, Status
  // Vamos buscar pelo nome da coluna para ser mais seguro
  const colNome = headers.indexOf('Nome do Atleta');
  const colNasc = headers.indexOf('Data Nasc');
  const colStatus = headers.indexOf('Status'); // Opcional
  
  if (colNome === -1 || colNasc === -1) {
    // Fallback: Tenta indices fixos se cabeçalhos não baterem
    // Python script create: A=ID, B=Nome, C=Data... (Indices 0, 1, 2)
    // Mas no Excel gerado começava na col 2 (B).
    // Vamos assumir: A=ID, B=Nome, C=Nasc
  }
  
  const athletes = [];
  
  // Começa do row 6 (dados) conforme script Python, ou row 1 ser data
  // Vamos varrer tudo a partir da linha 2
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const nome = row[1]; // Coluna B
    const nascRaw = row[2]; // Coluna C
    const status = row[5]; // Coluna F ('ATIVO')
    
    // Ignora se não tiver nome ou se Status != ATIVO (se existir coluna status)
    if (!nome) continue;
    if (colStatus !== -1 && String(status).toUpperCase() !== 'ATIVO') continue;
    
    // Extrair ano
    let year = 0;
    if (nascRaw instanceof Date) {
      year = nascRaw.getFullYear();
    } else if (typeof nascRaw === 'string') {
      // Tenta parsear "dd/mm/yyyy"
      const parts = nascRaw.split('/');
      if (parts.length === 3) year = parseInt(parts[2]);
    }
    
    // Verificar se ano está na lista target
    if (targetYears.includes(year)) {
      athletes.push({ nome: nome, ano: year });
    }
  }
  
  // Ordenar alfabético
  athletes.sort((a, b) => a.nome.localeCompare(b.nome));
  
  return athletes;
}
