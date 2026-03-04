%Partie 1 Code
for Nrs = 1:49
    
    % récupérer SUBJECT_i
    SUBJECT = eval(sprintf('SUBJECT_%d', Nrs));
    
    % FC
    SUBJECT.FC = corr(SUBJECT.TS);
    
    % SC déjà existante
    SC = SUBJECT.SC;
    
    fprintf('Sujet %d traité\n', Nrs);
    
    % remettre dans SUBJECT_i
    eval(sprintf('SUBJECT_%d = SUBJECT;', Nrs));
    
end

%Partie 2 Code
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

% Partie 3 modifiée : FC et SC sur la même figure

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
    
    % ---- Ligne 1 : FC ----
    subplot(2,3,k);
    imagesc(FC_mean);
    colorbar;
    clim([-1 1]);
    axis square;
    title(['FC moyenne - Quartile ' num2str(k)]);
    
    % ---- Ligne 2 : SC ----
    subplot(2,3,k+3);
    imagesc(log(SC_mean));
    colorbar;
    axis square;
    title(['SC moyenne (log) - Quartile ' num2str(k)]);
    
end

%Partie 4 Code
% --- FC Intra / Inter ---
left = 1:34;
right = 35:68;

intra_all = zeros(N,1);
inter_all = zeros(N,1);


for i = 1:Nrs
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    
    FC_LL = FC(left,left);
    FC_RR = FC(right,right);
    FC_LR = FC(left,right);
    
    mask_LL = ~eye(34);
    mask_RR = ~eye(34);
    
    intra = mean([mean(FC_LL(mask_LL)), mean(FC_RR(mask_RR))]);
    inter = mean(FC_LR(:));
    
    intra_all(i) = intra;
    inter_all(i) = inter;
    
end

% --- SC Intra / Inter ---

intra_SC_all = zeros(N,1);
inter_SC_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SC = SUBJECT.SC;
    
    SC_LL = SC(left,left);
    SC_RR = SC(right,right);
    SC_LR = SC(left,right);
    
    mask_LL = ~eye(34);
    mask_RR = ~eye(34);
    
    intra_SC = mean([mean(SC_LL(mask_LL)), mean(SC_RR(mask_RR))]);
    inter_SC = mean(SC_LR(:));
    
    intra_SC_all(i) = intra_SC;
    inter_SC_all(i) = inter_SC;
    
end

%stock pour chaque quartile
intra_q = zeros(3,1);
inter_q = zeros(3,1);

intra_SC_q = zeros(3,1);
inter_SC_q = zeros(3,1);

fprintf('\n')
fprintf('Connectivité Structurale par quartile\n')
fprintf('\n')

%Moy en fonction age moyen ?
age_q = zeros(3,1);

for k = 1:3
    
    idx = find(groups == k);
    
    % Âge moyen
    age_q(k) = mean(ages(idx));
    
    % FC
    intra_q(k) = mean(intra_all(idx));
    inter_q(k) = mean(inter_all(idx));
    
    % SC
    intra_SC_q(k) = mean(intra_SC_all(idx));
    inter_SC_q(k) = mean(inter_SC_all(idx));
    
    fprintf(['Quartile %d → Age: %.2f | FC Intra: %.3f | FC Inter: %.3f | ' ...
             'SC Intra: %.3f | SC Inter: %.3f\n'], ...
        k, age_q(k), ...
        intra_q(k), inter_q(k), ...
        intra_SC_q(k), inter_SC_q(k));
    
end
%Figure SC pas log
figure;
hold on;

plot(age_q, intra_SC_q, '-s', 'LineWidth', 2);
plot(age_q, inter_SC_q, '--s', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('Connectivité Structurale moyenne (log)');
title('SC vs âge (par quartile)');

legend('SC Intra','SC Inter');
grid on;

% Mise à l'échelle logarithmique de la SC
intra_SC_q = log(intra_SC_q);
inter_SC_q = log(inter_SC_q);

% FIGURE 1 : FC
figure;
hold on;

plot(age_q, intra_q, '-o', 'LineWidth', 2);
plot(age_q, inter_q, '--o', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('Connectivité Fonctionnelle moyenne');
title('FC vs âge (par quartile)');

legend('FC Intra','FC Inter');
grid on;

% FIGURE 2 : SC log
figure;
hold on;

plot(age_q, intra_SC_q, '-s', 'LineWidth', 2);
plot(age_q, inter_SC_q, '--s', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('Connectivité Structurale moyenne (log)');
title('SC log vs âge (par quartile)');

legend('SC Intra','SC Inter');
grid on;