# Модель, прогнозирующая успешность прохождения обучения студентов
[project](https://github.com/ghdena/Portfolio/blob/main/Online_course/Online_course.ipynb)

### Цель
Используя данные о первых двух днях на онлайн-курсе, предсказать, наберет ли пользователь 40 и более баллов. Качество модели оценить по метрике ROC-AUC.

### Инструменты
Python:
- sklearn (RandomizedSearchCV, RandomForestClassifier, GradientBoostingClassifier, LogisticRegression, StackingClassifier, StandardScaler, StratifiedKFold, RepeatedStratifiedKFold, cross_val_score, make_pipeline)
- xgboost (XGBClassifier)
- catboost (CatBoostClassifier)
- scipy.stats
- pandas
- numpy
- time

### Описание проекта и выводы
В данной работе проанализированы данные о решениях и действиях студентов за первые два дня прохождения онлайн-курса и созданы дополнительные признаки для обучения моделей.
При построении моделей были использованы алгоритмы: XGBClassifier, RandomForestClassifier, GradientBoostingClassifier, CatBoostClassifier и ансамбль Stacking.
Лучшей моделью, на основе максимальной нижней границы доверительного интервала ROC-AUC, оказался ансамбль Stacking. На тестовой выборке ROC-AUC - 0.8915.
