load C:\Users\aure6\Downloads\STAGE_M1\code\Workspace
%% =========================
% PARTIE 1 : FC
%% =========================
for Nrs = 1:49
    
    SUBJECT = eval(sprintf('SUBJECT_%d', Nrs));
    
    SUBJECT.FC = corr(SUBJECT.TS);
    
    eval(sprintf('SUBJECT_%d = SUBJECT;', Nrs));
    
end


%% =========================
% PARTIE 2 : GROUPES D'ÂGE
%% =========================
N = 49;
ages = zeros(N,1);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    ages(i) = SUBJECT.age;
end

q = quantile(ages, [0.333 0.666]);

groups = zeros(N,1);

for i = 1:N
    
    if ages(i) <= q(1)
        groups(i) = 1;
    elseif ages(i) <= q(2)
        groups(i) = 2;
    else
        groups(i) = 3;
    end
    
end

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SUBJECT.quartile = groups(i);
    eval(sprintf('SUBJECT_%d = SUBJECT;', i));
    
end

for k = 1:3
    fprintf('Quartile %d : %d sujets\n', k, sum(groups==k));
end


%% =========================
% PARTIE 3 : MATRICES MOYENNES
%% =========================
figure;

for k = 1:3
    
    FC_mean = zeros(68,68);
    SC_mean = zeros(68,68);
    count = 0;
    
    for i = 1:N
        
        if groups(i) == k
            
            SUBJECT = eval(sprintf('SUBJECT_%d', i));
            
            FC_mean = FC_mean + SUBJECT.FC;
            SC_mean = SC_mean + SUBJECT.SC;
            
            count = count + 1;
            
        end
        
    end
    
    FC_mean = FC_mean / count;
    SC_mean = SC_mean / count;
    
    subplot(2,3,k);
    imagesc(FC_mean);
    colorbar;
    clim([-1 1]);
    axis square;
    title(['FC moyenne - Quartile ' num2str(k)]);
    
    subplot(2,3,k+3);
    imagesc(log(SC_mean));
    colorbar;
    axis square;
    title(['SC moyenne (log) - Quartile ' num2str(k)]);
    
end


%% =========================
% PARTIE 4 : INTRA / INTER
%% =========================
left = 1:34;
right = 35:68;

intra_all = zeros(N,1);
inter_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    
    FC_LL = FC(left,left);
    FC_RR = FC(right,right);
    FC_LR = FC(left,right);
    
    mask = ~eye(34);
    
    intra = mean([mean(FC_LL(mask)), mean(FC_RR(mask))]);
    inter = mean(FC_LR(:));
    
    intra_all(i) = intra;
    inter_all(i) = inter;
    
end

% SC
intra_SC_all = zeros(N,1);
inter_SC_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SC = SUBJECT.SC;
    
    SC_LL = SC(left,left);
    SC_RR = SC(right,right);
    SC_LR = SC(left,right);
    
    mask = ~eye(34);
    
    intra_SC = mean([mean(SC_LL(mask)), mean(SC_RR(mask))]);
    inter_SC = mean(SC_LR(:));
    
    intra_SC_all(i) = intra_SC;
    inter_SC_all(i) = inter_SC;
    
end


%% =========================
% PARTIE 5 : MOYENNES + STD
%% =========================
intra_q = zeros(3,1);
inter_q = zeros(3,1);

intra_SC_q = zeros(3,1);
inter_SC_q = zeros(3,1);

std_intra_q = zeros(3,1);
std_inter_q = zeros(3,1);

std_intra_SC_q = zeros(3,1);
std_inter_SC_q = zeros(3,1);

age_q = zeros(3,1);

fprintf('\nConnectivité par quartile\n\n')

for k = 1:3
    
    idx = find(groups == k);
    
    age_q(k) = mean(ages(idx));
    
    % FC
    intra_q(k) = mean(intra_all(idx));
    inter_q(k) = mean(inter_all(idx));
    
    std_intra_q(k) = std(intra_all(idx));
    std_inter_q(k) = std(inter_all(idx));
    
    % SC
    intra_SC_q(k) = mean(intra_SC_all(idx));
    inter_SC_q(k) = mean(inter_SC_all(idx));
    
    std_intra_SC_q(k) = std(intra_SC_all(idx));
    std_inter_SC_q(k) = std(inter_SC_all(idx));
    
    fprintf(['Quartile %d → Age: %.2f | FC Intra: %.3f | FC Inter: %.3f | ' ...
             'SC Intra: %.3f | SC Inter: %.3f\n'], ...
        k, age_q(k), ...
        intra_q(k), inter_q(k), ...
        intra_SC_q(k), inter_SC_q(k));
    
end


%% =========================
% FIGURE FC + BARRES ERREUR
%% =========================
figure;
hold on;

errorbar(age_q, intra_q, 2*std_intra_q, '-o', 'LineWidth', 2);
errorbar(age_q, inter_q, 2*std_inter_q, '--o', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('Connectivité Fonctionnelle');
title('FC vs âge (par quartile)');

legend('FC Intra','FC Inter');
grid on;


%% =========================
% FIGURE SC (LOG) + ERREURS
%% =========================

% Passage au log
intra_SC_q_log = log(intra_SC_q);
inter_SC_q_log = log(inter_SC_q);

% Approximation propagation erreur
std_intra_SC_log = std_intra_SC_q ./ intra_SC_q;
std_inter_SC_log = std_inter_SC_q ./ inter_SC_q;

figure;
hold on;

errorbar(age_q, intra_SC_q_log, 2*std_intra_SC_log, '-s', 'LineWidth', 2);
errorbar(age_q, inter_SC_q_log, 2*std_inter_SC_log, '--s', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('SC (log)');
title('SC log vs âge (par quartile)');

legend('SC Intra','SC Inter');
grid on;