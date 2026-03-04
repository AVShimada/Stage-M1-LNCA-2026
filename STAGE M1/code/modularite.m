%% ================================
% PARAMÈTRES
% ================================
gamma   = 1;
n_runs  = 100;
tau     = 0.5;
reps    = 50;

N       = length(ages);
N_nodes = size(SUBJECT_1.FC,1);

%% ================================
% FC
% ================================
Q_FC  = zeros(N,1);
Ci_FC = zeros(N, N_nodes);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    FC(1:N_nodes+1:end) = 0;

    Ci_runs = zeros(n_runs, N_nodes);
    Q_runs  = zeros(n_runs,1);

    for r = 1:n_runs
        [Ci, Q] = community_louvain(FC, gamma, [], 'negative_sym');
        Ci_runs(r,:) = Ci;
        Q_runs(r) = Q;
    end

    % ===== CONSENSUS (VERSION ROBUSTE) =====
    D = agreement(Ci_runs');                 % co-classification
    Ci_consensus = consensus_und(D, tau, reps);

    Ci_FC(i,:) = Ci_consensus;
    Q_FC(i)    = mean(Q_runs);

    % affichage debug
    if i == 1
        figure;
        subplot(2,1,1)
        imagesc(Ci_runs)
        title('FC - Partitions (runs)')
        ylabel('Runs')
        xlabel('Noeuds')
        colorbar

        subplot(2,1,2)
        imagesc(Ci_consensus)
        title('FC - Consensus')
        xlabel('Noeuds')
        colorbar
    end
end

%% ================================
% SC
% ================================
Q_SC  = zeros(N,1);
Ci_SC = zeros(N, N_nodes);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SC = SUBJECT.SC;
    SC(1:N_nodes+1:end) = 0;
    W = log(SC + 1);

    Ci_runs = zeros(n_runs, N_nodes);
    Q_runs  = zeros(n_runs,1);

    for r = 1:n_runs
        [Ci, Q] = community_louvain(W, gamma);
        Ci_runs(r,:) = Ci;
        Q_runs(r) = Q;
    end

    D = agreement(Ci_runs');
    Ci_consensus = consensus_und(D, tau, reps);

    Ci_SC(i,:) = Ci_consensus;
    Q_SC(i)    = mean(Q_runs);
end

%% ================================
% MODULARITÉ vs ÂGE
% ================================
figure;
hold on;
scatter(ages, Q_FC, 50, 'filled');
p = polyfit(ages, Q_FC, 1);
xfit = linspace(min(ages), max(ages), 100);
yfit = polyval(p, xfit);
plot(xfit, yfit, 'LineWidth', 3);
xlabel('Âge');
ylabel('Modularité Q (FC)');
title('Modularité FC vs âge');
grid on;

figure;
hold on;
scatter(ages, Q_SC, 50, 'filled');
p = polyfit(ages, Q_SC, 1);
xfit = linspace(min(ages), max(ages), 100);
yfit = polyval(p, xfit);
plot(xfit, yfit, 'LineWidth', 3);
xlabel('Âge');
ylabel('Modularité Q (SC)');
title('Modularité SC vs âge');
grid on;

%% ================================
% NOMBRE DE MODULES
% ================================
n_modules_FC = zeros(N,1);
n_modules_SC = zeros(N,1);

for i = 1:N
    n_modules_FC(i) = length(unique(Ci_FC(i,:)));
    n_modules_SC(i) = length(unique(Ci_SC(i,:)));
end

figure;
scatter(ages, n_modules_FC, 50, 'filled');
xlabel('Âge');
ylabel('Nombre de modules (FC)');
title('Nombre de communautés FC vs âge');
grid on;

figure;
scatter(ages, n_modules_SC, 50, 'filled');
xlabel('Âge');
ylabel('Nombre de modules (SC)');
title('Nombre de communautés SC vs âge');
grid on;