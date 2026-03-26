%% =========================
% INTRA vs INTER MODULAR ANALYSIS
% (ROI-level approximation)
%% =========================

% Variables attendues :
% dimer_roi   : [49 x 68]
% trimer_roi  : [49 x 68]
% Ci          : [68 x 1]  -> module de chaque ROI
% group       : [49 x 1] ou [1 x 49]

%% =========================
% BASIC SIZES
%% =========================

nSub = size(dimer_roi,1);
nROI = size(dimer_roi,2);

if size(trimer_roi,1) ~= nSub || size(trimer_roi,2) ~= nROI
    error('dimer_roi et trimer_roi n''ont pas la même taille.');
end

group = group(:);
modules = Ci(:)';   % <- FIX IMPORTANT

if length(modules) ~= nROI
    error('Le vecteur Ci ne correspond pas au nombre de ROI.');
end

fprintf('Taille dimer_roi  : [%d x %d]\n', size(dimer_roi,1), size(dimer_roi,2));
fprintf('Taille trimer_roi : [%d x %d]\n', size(trimer_roi,1), size(trimer_roi,2));
fprintf('Taille modules    : [%d x %d]\n', size(modules,1), size(modules,2));

%% =========================
% COMPUTE INTRA / INTER PAR ROI
%% =========================

intra_dimer  = NaN(nSub, nROI);
inter_dimer  = NaN(nSub, nROI);

intra_trimer = NaN(nSub, nROI);
inter_trimer = NaN(nSub, nROI);

for r = 1:nROI
    
    same_module  = (modules == modules(r));
    other_module = (modules ~= modules(r));
    
    % enlever la ROI elle-même du intra
    same_module(r) = false;
    
    % intra
    if any(same_module)
        intra_dimer(:,r)  = mean(dimer_roi(:, same_module), 2, 'omitnan');
        intra_trimer(:,r) = mean(trimer_roi(:, same_module), 2, 'omitnan');
    end
    
    % inter
    if any(other_module)
        inter_dimer(:,r)  = mean(dimer_roi(:, other_module), 2, 'omitnan');
        inter_trimer(:,r) = mean(trimer_roi(:, other_module), 2, 'omitnan');
    end
end

fprintf('Intra/inter ROI-level calculés.\n');

%% =========================
% MOYENNE GLOBALE PAR SUJET
%% =========================

subj_intra_dimer  = mean(intra_dimer,  2, 'omitnan');
subj_inter_dimer  = mean(inter_dimer,  2, 'omitnan');

subj_intra_trimer = mean(intra_trimer, 2, 'omitnan');
subj_inter_trimer = mean(inter_trimer, 2, 'omitnan');

%% =========================
% STATS PAR GROUPE
%% =========================

nGroups = 3;

intra_d_mean  = NaN(nGroups,1);
inter_d_mean  = NaN(nGroups,1);
intra_t_mean  = NaN(nGroups,1);
inter_t_mean  = NaN(nGroups,1);

intra_d_sem   = NaN(nGroups,1);
inter_d_sem   = NaN(nGroups,1);
intra_t_sem   = NaN(nGroups,1);
inter_t_sem   = NaN(nGroups,1);

for g = 1:nGroups
    
    idx = (group == g);
    
    intra_d_mean(g) = mean(subj_intra_dimer(idx), 'omitnan');
    inter_d_mean(g) = mean(subj_inter_dimer(idx), 'omitnan');
    
    intra_t_mean(g) = mean(subj_intra_trimer(idx), 'omitnan');
    inter_t_mean(g) = mean(subj_inter_trimer(idx), 'omitnan');
    
    intra_d_sem(g) = std(subj_intra_dimer(idx), 'omitnan') / sqrt(sum(idx));
    inter_d_sem(g) = std(subj_inter_dimer(idx), 'omitnan') / sqrt(sum(idx));
    
    intra_t_sem(g) = std(subj_intra_trimer(idx), 'omitnan') / sqrt(sum(idx));
    inter_t_sem(g) = std(subj_inter_trimer(idx), 'omitnan') / sqrt(sum(idx));
end

%% =========================
% AFFICHAGE NUMERIQUE
%% =========================

fprintf('\n===== GROUP RESULTS =====\n');
for g = 1:nGroups
    fprintf('Groupe %d\n', g);
    fprintf('  Dimer  intra = %.4f ± %.4f\n', intra_d_mean(g), intra_d_sem(g));
    fprintf('  Dimer  inter = %.4f ± %.4f\n', inter_d_mean(g), inter_d_sem(g));
    fprintf('  Trimer intra = %.4f ± %.4f\n', intra_t_mean(g), intra_t_sem(g));
    fprintf('  Trimer inter = %.4f ± %.4f\n\n', inter_t_mean(g), inter_t_sem(g));
end

%% =========================
% FIGURE 1 : COURBES GLOBALES
%% =========================

figure('Name','Intra vs Inter - Global','Color','w');
hold on

x = 1:nGroups;

errorbar(x, intra_d_mean, intra_d_sem, '-o', 'LineWidth', 2, 'MarkerSize', 7)
errorbar(x, inter_d_mean, inter_d_sem, '--o', 'LineWidth', 2, 'MarkerSize', 7)

errorbar(x, intra_t_mean, intra_t_sem, '-s', 'LineWidth', 2, 'MarkerSize', 7)
errorbar(x, inter_t_mean, inter_t_sem, '--s', 'LineWidth', 2, 'MarkerSize', 7)

xticks([1 2 3])
xticklabels({'Jeune','Moyen','Agée'})

ylabel('Strength')
title('Intra vs Inter Modular Strength')
legend({'Dimer Intra','Dimer Inter','Trimer Intra','Trimer Inter'}, 'Location','best')
grid on
box off

%% =========================
% FIGURE 2 : BARPLOT
%% =========================

figure('Name','Intra vs Inter - Bars','Color','w')

colors = [
    0.00 0.60 0.30
    0.80 0.80 0.20
    0.85 0.33 0.10
];

subplot(1,2,1)
hold on

x_intra = [1 2 3];
x_inter = [1.35 2.35 3.35];

for g = 1:nGroups
    bar(x_intra(g), intra_d_mean(g), 0.28, 'FaceColor', colors(g,:), 'EdgeColor', 'none');
    bar(x_inter(g), inter_d_mean(g), 0.28, 'FaceColor', colors(g,:)*0.6 + 0.4, 'EdgeColor', 'none');
end

errorbar(x_intra, intra_d_mean, intra_d_sem, 'k', 'LineStyle','none', 'LineWidth',1)
errorbar(x_inter, inter_d_mean, inter_d_sem, 'k', 'LineStyle','none', 'LineWidth',1)

xticks([1.175 2.175 3.175])
xticklabels({'Jeune','Moyen','Agée'})
ylabel('Dimer strength')
title('Dimer : Intra vs Inter')
legend({'Intra','Inter'}, 'Location','best')
grid on
box off

subplot(1,2,2)
hold on

for g = 1:nGroups
    bar(x_intra(g), intra_t_mean(g), 0.28, 'FaceColor', colors(g,:), 'EdgeColor', 'none');
    bar(x_inter(g), inter_t_mean(g), 0.28, 'FaceColor', colors(g,:)*0.6 + 0.4, 'EdgeColor', 'none');
end

errorbar(x_intra, intra_t_mean, intra_t_sem, 'k', 'LineStyle','none', 'LineWidth',1)
errorbar(x_inter, inter_t_mean, inter_t_sem, 'k', 'LineStyle','none', 'LineWidth',1)

xticks([1.175 2.175 3.175])
xticklabels({'Jeune','Moyen','Agée'})
ylabel('Trimer strength')
title('Trimer : Intra vs Inter')
legend({'Intra','Inter'}, 'Location','best')
grid on
box off

sgtitle('Intra vs Inter Modular Analysis')

%% =========================
% FIGURE 3 : PAR MODULE (AVEC BARRES D'ERREUR)
%% =========================

unique_modules = unique(modules);
nMod = length(unique_modules);

module_intra_d = NaN(nGroups, nMod);
module_inter_d = NaN(nGroups, nMod);
module_intra_t = NaN(nGroups, nMod);
module_inter_t = NaN(nGroups, nMod);

% 👉 SEM
module_intra_d_sem = NaN(nGroups, nMod);
module_inter_d_sem = NaN(nGroups, nMod);
module_intra_t_sem = NaN(nGroups, nMod);
module_inter_t_sem = NaN(nGroups, nMod);

for im = 1:nMod
    
    m = unique_modules(im);
    roi_idx = (modules == m);
    
    subj_mod_intra_d = mean(intra_dimer(:, roi_idx), 2, 'omitnan');
    subj_mod_inter_d = mean(inter_dimer(:, roi_idx), 2, 'omitnan');
    
    subj_mod_intra_t = mean(intra_trimer(:, roi_idx), 2, 'omitnan');
    subj_mod_inter_t = mean(inter_trimer(:, roi_idx), 2, 'omitnan');
    
    for g = 1:nGroups
        idx = (group == g);
        
        % ===== MEAN =====
        module_intra_d(g,im) = mean(subj_mod_intra_d(idx), 'omitnan');
        module_inter_d(g,im) = mean(subj_mod_inter_d(idx), 'omitnan');
        
        module_intra_t(g,im) = mean(subj_mod_intra_t(idx), 'omitnan');
        module_inter_t(g,im) = mean(subj_mod_inter_t(idx), 'omitnan');
        
        % ===== SEM =====
        module_intra_d_sem(g,im) = std(subj_mod_intra_d(idx), 'omitnan') / sqrt(sum(idx));
        module_inter_d_sem(g,im) = std(subj_mod_inter_d(idx), 'omitnan') / sqrt(sum(idx));
        
        module_intra_t_sem(g,im) = std(subj_mod_intra_t(idx), 'omitnan') / sqrt(sum(idx));
        module_inter_t_sem(g,im) = std(subj_mod_inter_t(idx), 'omitnan') / sqrt(sum(idx));
    end
end

figure('Name','Intra vs Inter by Module','Color','k')

ncols = ceil(sqrt(nMod));
nrows = ceil(nMod / ncols);

for im = 1:nMod
    
    subplot(nrows, ncols, im)
    hold on
    
    x = 1:nGroups;
    
    % ===== COURBES =====
    plot(x, module_intra_d(:,im), '-o', 'LineWidth', 1.8)
    plot(x, module_inter_d(:,im), '--o', 'LineWidth', 1.8)
    plot(x, module_intra_t(:,im), '-s', 'LineWidth', 1.8)
    plot(x, module_inter_t(:,im), '--s', 'LineWidth', 1.8)
    
    % ===== BARRES D'ERREUR BLANCHES =====
    errorbar(x, module_intra_d(:,im), module_intra_d_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    errorbar(x, module_inter_d(:,im), module_inter_d_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    
    errorbar(x, module_intra_t(:,im), module_intra_t_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    errorbar(x, module_inter_t(:,im), module_inter_t_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(sprintf('Module %d', unique_modules(im)))
    
    grid on
    box off
end

sgtitle('Intra vs Inter per Module (avec SEM)')

fprintf('\n===== DONE =====\n');