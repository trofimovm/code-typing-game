#!/bin/bash
# Скрипт для исправления подсчета раундов во всех играх

echo "Исправление cloud-architect.html..."

# 1. Добавить roundsCompleted variable
sed -i '' 's/let currentRound = 0;/let currentRound = 0;\n        let roundsCompleted = 0; \/\/ Count of successfully completed rounds/' cloud-architect.html

# 2. Добавить roundsCompleted++ в roundComplete()
sed -i '' '/document\.getElementById('\''feedback'\'')\.className = '\''feedback perfect'\'';/a\
\
            roundsCompleted++; \/\/ Increment completed rounds counter
' cloud-architect.html

# 3. Добавить roundsCompleted = 0 в start functions
sed -i '' '/function startArchitectGame/,/nextRound();/{
    s/currentRound = 0;/currentRound = 0;\n            roundsCompleted = 0;/
}' cloud-architect.html

# 4. Использовать roundsCompleted в showFinalScreen
sed -i '' "s/getElementById('finalRoundsCompleted').textContent = currentRound;/getElementById('finalRoundsCompleted').textContent = roundsCompleted;/g" cloud-architect.html
sed -i '' 's/Вы исправили \${currentRound}/Вы исправили ${roundsCompleted}/g' cloud-architect.html
sed -i '' 's/currentRound === 1/roundsCompleted === 1/g' cloud-architect.html
sed -i '' 's/currentRound < 5/roundsCompleted < 5/g' cloud-architect.html
sed -i '' 's/Пройдено уровней: \${currentRound}\/7/Пройдено уровней: ${roundsCompleted}\/7/g' cloud-architect.html

echo "cloud-architect.html исправлен!"

echo "Исправление speed-typing.html..."

# То же для speed-typing.html
sed -i '' 's/let currentRound = 0;/let currentRound = 0;\n        let roundsCompleted = 0; \/\/ Count of successfully completed rounds/' speed-typing.html
sed -i '' '/document\.getElementById('\''feedback'\'')\.className = '\''feedback perfect'\'';/a\
\
            roundsCompleted++; \/\/ Increment completed rounds counter
' speed-typing.html
sed -i '' '/function startTypingGame/,/nextRound();/{
    s/currentRound = 0;/currentRound = 0;\n            roundsCompleted = 0;/
}' speed-typing.html
sed -i '' "s/getElementById('finalRoundsCompleted').textContent = currentRound;/getElementById('finalRoundsCompleted').textContent = roundsCompleted;/g" speed-typing.html

echo "speed-typing.html исправлен!"
echo "✅ Все файлы исправлены!"
