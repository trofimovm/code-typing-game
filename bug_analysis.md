# Анализ текущих багов на множественность решений

## Баг 1: Забыт return
**Проблема:** Можно решить минимум 2 способами
```javascript
function add(a, b) {
  const result = a + b;
  // забыли return
}
```
Решения:
- ❌ `return result;` (ожидаемое)
- ❌ `return a + b;` (альтернатива)

**Вывод:** ПРОБЛЕМАТИЧНЫЙ

## Баг 2: Фильтр без return
**Проблема:** Можно решить минимум 2 способами
```javascript
const even = numbers.filter(n => {
  n % 2 === 0;
});
```
Решения:
- ❌ `return n % 2 === 0;` (ожидаемое)
- ❌ `numbers.filter(n => n % 2 === 0)` (убрать скобки)

**Вывод:** ПРОБЛЕМАТИЧНЫЙ

## Баг 3: Бесконечный цикл
**Проблема:** Можно решить минимум 4 способами
```javascript
let count = 0;
while (count < 5) {
  console.log(count);
  // забыли инкремент
}
```
Решения:
- ❌ `count++;`
- ❌ `++count;`
- ❌ `count += 1;`
- ❌ `count = count + 1;`

**Вывод:** ОЧЕНЬ ПРОБЛЕМАТИЧНЫЙ

## Баг 4: Забыт await
**Проблема:** Решение относительно однозначно
```javascript
async function getData() {
  const response = fetch('/api/data');
  const data = response.json();
  return data;
}
```
Решение:
- ✅ Добавить `await` перед `fetch` и `response.json()` - ЕДИНСТВЕННЫЙ способ

**Вывод:** ХОРОШИЙ БАГ ✓

## Баг 5: Мутация объекта
**Проблема:** Можно решить несколькими способами
```javascript
function updateCount(newCount) {
  state.count = newCount;
  return state;
}
```
Решения:
- ❌ `{ ...state, count: newCount }`
- ❌ `Object.assign({}, state, { count: newCount })`

**Вывод:** ПРОБЛЕМАТИЧНЫЙ

---

# Предложения новых багов с ОДНОЗНАЧНЫМ решением

## Тип 1: Опечатка в ключевом слове
```javascript
fucntion add(a, b) {  // опечатка в function
  return a + b;
}
```
Решение: `fucntion` → `function` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 2: Опечатка в имени переменной
```javascript
const items = [1, 2, 3];
return itmes.length;  // опечатка
```
Решение: `itmes` → `items` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 3: Неправильный оператор
```javascript
if (age = 18) {  // присваивание вместо сравнения
  return 'adult';
}
```
Решение: `=` → `===` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 4: Неправильная индексация
```javascript
const first = arr[1];  // второй элемент вместо первого
```
Решение: `[1]` → `[0]` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 5: Неправильный метод массива
```javascript
const doubled = arr.forEach(x => x * 2);  // forEach не возвращает массив
```
Решение: `forEach` → `map` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 6: Неправильный порядок операндов
```javascript
function divide(a, b) {
  return b / a;  // перепутаны местами
}
```
Решение: `b / a` → `a / b` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 7: Неправильное условие (знак)
```javascript
while (count > 5) {  // неправильный знак
  console.log(count);
  count++;
}
```
Решение: `>` → `<` - ТОЛЬКО ОДИН СПОСОБ ✓

## Тип 8: Опечатка в методе
```javascript
const upper = str.toUperCase();  // опечатка в методе
```
Решение: `toUperCase` → `toUpperCase` - ТОЛЬКО ОДИН СПОСОБ ✓
