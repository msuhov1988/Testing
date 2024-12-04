const ID = {
    firstDateInput: "#first-date",
    secondDateInput: "#second-date",
    loadButton: "#load",
    periodSpan: "#selected-period",
    errorSpan: "#error-field",
    table: "#table",
}

const META_URL = "/meta";
const PERIOD_URL = "/period/";

const REQ_NAMES = ["Загруженных заявок",
                   "Дубли",
                   "На создание",
                   "На расширение",
                   "Обработка завершена",
                   "Возвращена на уточнение",
                   "Отправлена в обработку",
                   "Пакетов",
                   "Пользователей"]

const ROW_TEMPLATE = document.createElement("template");
ROW_TEMPLATE.innerHTML = `<tr> <td></td><td></td><td></td> </tr>`

async function getMeta() {
    const response = await fetch(META_URL);
    if (response.ok && response.headers.get("Content-Type") === "application/json") {
        let result = await response.json();
        if (Array.isArray(result) && result.length === 3) {
            const [minDate, maxDate, totals] = result;
            return [[minDate, maxDate, totals], null]
        } else {
            return [null, `Формат данных с сервера не соответствует ожидаемому`]
        }
    } else {
        return [null, `При запросе метаданных получен некорректный ответ от сервера: ${response.status}`]
    }
}


function writeTotalsToTable(quantities, tableBody, errorLabel) {
    if (REQ_NAMES.length !== quantities.length) {
        errorLabel.textContent = `Размер данных по количествам ${quantities.length}, а должен быть ${REQ_NAMES.length}`;
    } else {
        quantities.forEach((qnt, i) => {
            let fragment = ROW_TEMPLATE.content.cloneNode(true);
            let tr = fragment.firstElementChild;
            let [tdReq, tdTotals] = [tr.firstElementChild, tr.lastElementChild];
            tdReq.textContent = REQ_NAMES[i];
            tdTotals.textContent = qnt;
            tableBody.append(fragment);
        })
    }
}

function getData(firstPeriodInput, secondPeriodInput, tableBody, errorLabel, loadButton) {
    const [firstInput, secondInput, tBody, eLabel, button] = [firstPeriodInput, secondPeriodInput, tableBody, errorLabel, loadButton];
    async function getDataInner() {
        const firstDt = (firstInput.value) ? firstInput.value : firstInput.min;
        const secondDt = (secondInput.value) ? secondInput.value : secondInput.max;
        button.disabled = true;
        button.style = {opacity: "0.5"};
        button.style.cursor = 'pointer';
        const response = await fetch(PERIOD_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify([firstDt, secondDt])
        });
        if (response.ok && response.headers.get("Content-Type") === "application/json") {
            let answer = await response.json();
            let [result, error] = answer;
            if (error) { eLabel.textContent = error }
            else { writePeriodDataToTable(result, tBody, eLabel) }
        } else {
            eLabel.textContent = `Некорректный ответ от сервера: ${response.status} код HTTP`;
        }
        button.disabled = false;
        button.style = {opacity: "1"};
        button.style.cursor = 'default';
    }
    return getDataInner
}

function writePeriodDataToTable(quantities, tableBody, errorLabel) {
    if (REQ_NAMES.length !== quantities.length) {
        errorLabel.textContent = `Размер данных по количествам ${quantities.length}, а должен быть ${REQ_NAMES.length}`;
    } else {
        quantities.forEach((qnt, i) => {
            const tr = tableBody.children[i];
            const tdPeriodData = tr.firstElementChild.nextElementSibling;
            tdPeriodData.textContent = (qnt === 0) ? "-" : qnt;
        })
    }
}

function viewPeriod(firstPeriodInput, secondPeriodInput, periodLabel, loadButton) {
    const [firstInput, secondInput, label, button] = [firstPeriodInput, secondPeriodInput, periodLabel, loadButton];
    function viewPeriodInner() {
        const [first, second] = [firstInput.value, secondInput.value];
        if (!first && !second) { label.textContent = `Период:  все` }
        else if (!first) {
            let secondDt = new Date(second);
            label.textContent = `Период: по ${secondDt.getDate()}.${secondDt.getMonth() + 1}.${secondDt.getFullYear()}`;
        }
        else if (!second) {
            let firstDt = new Date(first);
            label.textContent = `Период: с ${firstDt.getDate()}.${firstDt.getMonth() + 1}.${firstDt.getFullYear()}`; }
        else {
            let firstDt = new Date(first);
            let secondDt = new Date(second);
            if (firstDt > secondDt) {
                label.textContent = ``;
                button.disabled = true;
                button.style = {opacity: "0.5"};
                return
            }
            let firstLabel = `${firstDt.getDate()}.${firstDt.getMonth() + 1}.${firstDt.getFullYear()}`;
            let secondLabel = `${secondDt.getDate()}.${secondDt.getMonth() + 1}.${secondDt.getFullYear()}`;
            label.textContent = `Период: с ${firstLabel} по  ${secondLabel}`;
        }
        button.disabled = false;
        button.style = {opacity: "1"};
    }
    return viewPeriodInner
}


async function main() {
    const htmlFirstDate = document.querySelector(`${ID.firstDateInput}`);
    const htmlSecondDate = document.querySelector(`${ID.secondDateInput}`);
    const htmlPeriodLabel = document.querySelector(`${ID.periodSpan}`);
    const htmlErrorLabel = document.querySelector(`${ID.errorSpan}`);
    const htmlButton = document.querySelector(`${ID.loadButton}`);
    const htmlTableBody = document.querySelector(`${ID.table} tbody`);
    htmlButton.disabled = true;
    htmlButton.style = {opacity: "0.5"};
    const [meta, error] = await getMeta();
    if (error) { htmlErrorLabel.textContent = error; return }
    htmlButton.disabled = false;
    htmlButton.style = {opacity: "1"};
    const [minDate, maxDate, totals] = meta;
    htmlFirstDate.min = minDate;
    htmlFirstDate.max = maxDate;
    htmlSecondDate.min = minDate;
    htmlSecondDate.max = maxDate;
    writeTotalsToTable(totals, htmlTableBody, htmlErrorLabel);
    document.addEventListener("input", viewPeriod(htmlFirstDate, htmlSecondDate, htmlPeriodLabel, htmlButton))
    htmlButton.addEventListener("click", getData(htmlFirstDate, htmlSecondDate, htmlTableBody, htmlErrorLabel, htmlButton))
}

window.addEventListener("load", main)
