%% ========================================================================
%  META-HUBS + VALEURS BRUTES + BARRES D'ERREUR
%% ========================================================================

fprintf('\n===== META-HUBS (RAW VALUES + SEM) =====\n')

%% =========================
% ROI NAMES
%% =========================

ROI_names = cell(1, 68);
k = 1;

for i = 1:length(regions_base)
    ROI_names{k}   = [regions_base{i} '_L'];
    ROI_names{k+1} = [regions_base{i} '_R'];
    k = k + 2;
end

ROI_names = ROI_names(1:nROI);

%% =========================
% META-HUBS (BASED ON TRIMERS)
%% =========================

trimer_importance = mean(trimer_group,1);

threshold = prctile(trimer_importance, 80);
meta_hubs = find(trimer_importance >= threshold);

fprintf('Meta-hubs: %d / %d\n', length(meta_hubs), nROI)

%% =========================
% COMPUTE MEAN + SEM PAR GROUPE
%% =========================

dimer_mean  = zeros(3,nROI);
dimer_sem   = zeros(3,nROI);

trimer_mean = zeros(3,nROI);
trimer_sem  = zeros(3,nROI);

for g = 1:3
    
    idx = group == g;
    
    dimer_mean(g,:)  = mean(dimer_roi(idx,:),1);
    trimer_mean(g,:) = mean(trimer_roi(idx,:),1);
    
    dimer_sem(g,:)  = std(dimer_roi(idx,:),[],1) ./ sqrt(sum(idx));
    trimer_sem(g,:) = std(trimer_roi(idx,:),[],1) ./ sqrt(sum(idx));
    
end

%% =========================
% SUBPLOT ORGANISATION
%% =========================

nHubs = length(meta_hubs);
ncols = ceil(sqrt(nHubs));
nrows = ceil(nHubs / ncols);

colors = [ ...
    0 0.6 0.3;    % G1 (vert comme papier)
    0.8 0.8 0.2;  % G2 (jaune)
    0.85 0.33 0.10 % G3 (orange/rouge)
];

%% =========================
% FIGURE DIMERS
%% =========================

figure('Name','Dimers (Meta-hubs)','Color','k')

for idx = 1:nHubs
    
    r = meta_hubs(idx);
    
    subplot(nrows, ncols, idx)
    hold on
    
    vals = dimer_mean(:,r);
    err  = dimer_sem(:,r);
    
    for g = 1:3
        bar(g, vals(g), 'FaceColor', colors(g,:), 'EdgeColor','none')
    end
    
    errorbar(1:3, vals, err, 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'}) % adapte si besoin
    
    title(ROI_names{r}, 'Interpreter','none')
    
    ylim([0 0.6])
    grid on
    
end

sgtitle('Interzone Dimer Strength (Meta-hubs)')

%% =========================
% FIGURE TRIMERS
%% =========================

figure('Name','Trimers (Meta-hubs)','Color','k')

for idx = 1:nHubs
    
    r = meta_hubs(idx);
    
    subplot(nrows, ncols, idx)
    hold on
    
    vals = trimer_mean(:,r);
    err  = trimer_sem(:,r);
    
    for g = 1:3
        bar(g, vals(g), 'FaceColor', colors(g,:), 'EdgeColor','none')
    end
    
    errorbar(1:3, vals, err, 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(ROI_names{r}, 'Interpreter','none')
    
    ylim([0 0.6]) % ⚠️ important pour voir négatif
    grid on
    
end

sgtitle('Interzone Trimer Strength (Meta-hubs)')

fprintf('\n===== DONE =====\n')