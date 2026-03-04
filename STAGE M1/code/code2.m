%% =========================
% PARAMÈTRES
%% =========================
N_nodes = 68;

strength_FC = zeros(N, N_nodes);
strength_SC = zeros(N, N_nodes);


%% =========================
% CALCUL DES FORCES (FC + SC LOG)
%% =========================
for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    
    FC = SUBJECT.FC;
    SC = SUBJECT.SC;
    
    % enlever diagonale
    FC(1:N_nodes+1:end) = 0;
    SC(1:N_nodes+1:end) = 0;
    
    % FC classique
    strength_FC(i,:) = sum(FC, 2);
    
    % SC en LOG (IMPORTANT)
    strength_SC(i,:) = sum(log(SC + 1), 2);
    
end


%% =========================
% RÉGRESSION PAR NŒUD
%% =========================
slopes_FC = zeros(N_nodes,1);
pvals_FC = zeros(N_nodes,1);

slopes_SC = zeros(N_nodes,1);
pvals_SC = zeros(N_nodes,1);

for n = 1:N_nodes
    
    X = [ones(N,1), ages];
    
    % ===== FC =====
    y = strength_FC(:,n);
    
    b = X \ y;
    slopes_FC(n) = b(2);
    
    mdl = fitlm(ages, y);
    pvals_FC(n) = mdl.Coefficients.pValue(2);
    
    % ===== SC (log) =====
    y2 = strength_SC(:,n);
    
    b2 = X \ y2;
    slopes_SC(n) = b2(2);
    
    mdl2 = fitlm(ages, y2);
    pvals_SC(n) = mdl2.Coefficients.pValue(2);
    
end


%% =========================
% PLOT DES PENTES
%% =========================
figure;
bar(slopes_FC);
xlabel('Nœuds');
ylabel('Pente');
title('Effet de l''âge sur FC');
grid on;

figure;
bar(slopes_SC);
xlabel('Nœuds');
ylabel('Pente (log)');
title('Effet de l''âge sur SC (log)');
grid on;


%% =========================
% NŒUDS SIGNIFICATIFS
%% =========================
alpha = 0.05;

sig_nodes_FC = find(pvals_FC < alpha);
sig_nodes_SC = find(pvals_SC < alpha);

fprintf('Nœuds FC significatifs :\n');
disp(sig_nodes_FC');

fprintf('Nœuds SC significatifs :\n');
disp(sig_nodes_SC');


%% =========================
% COURBES LISSÉES FC
%% =========================
figure;
hold on;

for n = 1:N_nodes
    
    y = strength_FC(:,n);
    
    [ages_sorted, idx] = sort(ages);
    y_sorted = y(idx);
    
    y_smooth = smooth(ages_sorted, y_sorted, 0.3, 'loess');
    
    plot(ages_sorted, y_smooth, 'LineWidth', 1);
    
end

xlabel('Âge');
ylabel('Force FC');
title('Évolution des 68 nœuds FC (LOESS)');
grid on;


%% =========================
% COURBES LISSÉES SC (LOG)
%% =========================
figure;
hold on;

for n = 1:N_nodes
    
    y = strength_SC(:,n); % déjà en log
    
    [ages_sorted, idx] = sort(ages);
    y_sorted = y(idx);
    
    y_smooth = smooth(ages_sorted, y_sorted, 0.3, 'loess');
    
    plot(ages_sorted, y_smooth, 'LineWidth', 1);
    
end

xlabel('Âge');
ylabel('Force SC (log)');
title('Évolution des 68 nœuds SC (log, LOESS)');
grid on;